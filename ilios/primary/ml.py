import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import LabelEncoder
from primary.models import Profile, Event, LikedEvent, ProfileDetail, RegisteredEvent, CompletedEvent
import os

def run_recommendation_model_for_user(target_user_id, interactions_data, event_tags, user_interests, collaborative_weight=0.5, keyword_weight=0.5):
    print(target_user_id)
    print(interactions_data)
    print(event_tags)
    print(user_interests)
    all_events = set(interactions_data['event_id']).union(event_tags.keys())
    all_events = sorted(all_events)

    event_encoder = LabelEncoder()
    user_encoder = LabelEncoder()

    interactions_data['event_id'] = event_encoder.fit_transform(interactions_data['event_id'])
    interactions_data['user_id'] = user_encoder.fit_transform(interactions_data['user_id'])

    for event_id in event_tags:
        if event_id not in all_events:
            all_events.append(event_id)

    all_events = sorted(all_events)

    for user_id in user_interests:
        for event_id in event_tags:
            if event_id not in user_interests[user_id]:
                user_interests[user_id].append(event_id)

    num_events = len(all_events)
    num_users = len(user_encoder.classes_)

    target_user_encoded = user_encoder.transform([target_user_id])[0]

    embedding_size = 30
    model = NeuralMatrixFactorizationWithMLP(num_users, num_events, embedding_size)
    model.compile(optimizer='adam', loss='mse')

    checkpoint_dir = './model_checkpoints'
    os.makedirs(checkpoint_dir, exist_ok=True)

    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        filepath=os.path.join(checkpoint_dir, 'model_checkpoint.weights.h5'),
        save_weights_only=True,
        verbose=1
    )

    model_input = interactions_data[['user_id', 'event_id']].values
    model.fit(
        model_input,
        interactions_data['rating'].values,
        batch_size=64,
        epochs=10,
        callbacks=[checkpoint_callback],
        verbose=0
    )

    latest_checkpoint = tf.train.latest_checkpoint(checkpoint_dir)
    if latest_checkpoint:
        model.load_weights(latest_checkpoint)

    target_user_events = np.arange(num_events)
    target_user_input = np.array([(target_user_encoded, event_id) for event_id in target_user_events])
    target_user_recommendations = model.predict(target_user_input).reshape(1, -1)

    if target_user_recommendations.shape[1] != num_events:
        target_user_recommendations = np.zeros((1, num_events))

    user_similarities = calculate_user_similarity(target_user_id, interactions_data, event_tags, user_interests, num_users, num_events)

    keyword_similarity = calculate_keyword_similarity(target_user_id, event_tags, user_interests, num_events)

    combined_similarity = collaborative_weight * user_similarities[target_user_encoded] + keyword_weight * keyword_similarity[0]

    target_user_recommendations += combined_similarity

    print("Finsihed!")

    return target_user_recommendations

def calculate_user_similarity(target_user_id, interactions_data, event_tags, user_interests, num_users, num_events):
    user_similarity = np.zeros((num_users, num_events))
    print(target_user_id.split()[-1])
    target_user_idx = int(target_user_id.split()[-1]) - 1
    target_user_interests_set = set(user_interests.get(target_user_id, []))
    for user_id in range(num_users):
        if user_id == target_user_idx:
            continue
        user_interests_set = set(user_interests.get(f'User {user_id + 1}', []))
        user_similarity_scores = [len(target_user_interests_set.intersection(user_interests_set))]
        user_similarity[user_id] = np.max(user_similarity_scores)
    return user_similarity

def calculate_keyword_similarity(target_user_id, event_tags, user_interests, num_events):
    keyword_similarity = np.zeros((1, num_events))
    target_user_interests_set = set(user_interests.get(target_user_id, []))
    for event_id in range(num_events):
        event_tags_set = set(event_tags.get(f'Event {event_id + 1}', []))
        keyword_similarity_scores = [len(target_user_interests_set.intersection(event_tags_set))]
        keyword_similarity[0, event_id] = np.max(keyword_similarity_scores)
    return keyword_similarity

class NeuralMatrixFactorizationWithMLP(tf.keras.Model):
    def __init__(self, num_users, num_items, embedding_size=30):
        super(NeuralMatrixFactorizationWithMLP, self).__init__()
        self.user_embedding_gmf = tf.keras.layers.Embedding(num_users, embedding_size,
                                                            embeddings_regularizer=tf.keras.regularizers.l2(1e-6))
        self.item_embedding_gmf = tf.keras.layers.Embedding(num_items, embedding_size,
                                                            embeddings_regularizer=tf.keras.regularizers.l2(1e-6))
        self.user_embedding_mlp = tf.keras.layers.Embedding(num_users, embedding_size,
                                                            embeddings_regularizer=tf.keras.regularizers.l2(1e-6))
        self.item_embedding_mlp = tf.keras.layers.Embedding(num_items, embedding_size,
                                                            embeddings_regularizer=tf.keras.regularizers.l2(1e-6))

        self.mlp_layers = tf.keras.Sequential([
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(32, activation='relu')
        ])
        self.concat_layers = tf.keras.layers.Concatenate()
        self.final_dense = tf.keras.layers.Dense(1)

    def call(self, inputs):
        user_ids = inputs[:, 0]
        event_ids = inputs[:, 1]

        user_embed_gmf = self.user_embedding_gmf(user_ids)
        item_embed_gmf = self.item_embedding_gmf(event_ids)
        user_embed_mlp = self.user_embedding_mlp(user_ids)
        item_embed_mlp = self.item_embedding_mlp(event_ids)

        mf_output = tf.multiply(user_embed_gmf, item_embed_gmf)

        mlp_output = self.mlp_layers(self.concat_layers([user_embed_mlp, item_embed_mlp]))

        concat_output = tf.concat([mf_output, mlp_output], axis=1)

        output = self.final_dense(concat_output)
        return output

# interactions_data = pd.DataFrame({
#     'user_id': ['User 1', 'User 2', 'User 3', 'User 1', 'User 2', 'User 3'], 
#     'event_id': ['Event 1', 'Event 1', 'Event 1', 'Event 2', 'Event 2', 'Event 2'], 
#     'rating': [5, 4, 3, 4, 3, 2]  
# })

# event_tags = {
#     'Event 1': ['coding', 'python programming'],
#     'Event 2': ['data science', 'machine learning'],
#     'Event 3': ['web development', 'javascript'],
#     'Event 4': ['networking', 'cybersecurity'],
#     'Event 5': ['artificial intelligence', 'robotics']
# }

# user_interests = {
#     'User 1': ['programming', 'machine learning'],
#     'User 2': ['data science', 'networking'],
#     'User 3': ['web development', 'coding']
# }

profile_set = ProfileDetail.objects.all()

user_interests = {}
data = []
event_tags = {}

for i in profile_set:
    profile = i.user_profile
    interests = i.interests
    user_interests.update({profile.user.username:interests})

for target_prof_details in profile_set:
    for x in CompletedEvent.objects.all():
        prof_details = x.event_data.user_profile
        event = x.event_data.event
        event_tags.update({event.title:event.tags})
        if prof_details == target_prof_details:
            data.append(
                {
                    'user_id': prof_details.user_profile.user.username,
                    'event_id': event.title,
                    'rating': x.rating,
                }
            )


interactions_data = pd.DataFrame(data)

# Example usage:
target_user_id = 'cal'
target_user_recommendations = run_recommendation_model_for_user(target_user_id, interactions_data, event_tags, user_interests, collaborative_weight=0.7, keyword_weight=0.3)

print("Recommendations for", target_user_id + ":")
for event_id, rating in enumerate(target_user_recommendations[0], start=1):
    print(f"Event {event_id}: {rating}")

likeliness_scores = 1 / (1 + np.exp(-target_user_recommendations))

print("\nLikeliness of participating in events for", target_user_id + ":")
for event_id, likeliness in enumerate(likeliness_scores[0], start=1):
    print(f"Event {event_id}: {likeliness}")

def finalFunc(target_user_id=target_user_id, target_user_recommendations=target_user_recommendations):
    likeliness_scores = 1 / (1 + np.exp(-target_user_recommendations))
    print("\nLikeliness of participating in events for", target_user_id + ":")
    for event_id, likeliness in enumerate(likeliness_scores[0], start=1):
        print(f"Event {event_id}: {likeliness}")


