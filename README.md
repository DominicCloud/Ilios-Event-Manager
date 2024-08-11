# ilios Event-Manager
 
**college Event Management application** complete with a myriad of features, build with Django + Tailwind
Website is built with a minimalistic design by adopting a *neo-brutalism* style

Prominent features include:
- Posting, liking and registering of events
- Sections off userbase between regular Users and College Hosts
- Add-on features such as ratings and review threads on events
- Data Visualisation available for College Hosts

**Note:**
After relocating code, make sure to update the *settings.py* file, in order to update specific variables, namely
EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, SECRET_KEY.
You may choose to use values of your own for these variables.

SECRET_KEY is compulsory for any django project.
EMAIL_HOST_USER, EMAIL_HOST_PASSWORD are only used for the optional email notification feature.
If you do not wish to use the additional email functionality present provided in the project, go to "Ilios-Event-Manager/ilios/primary
/views.py" and delete the following functions:
- created_success_mail()
- register_success_mail()

Your project should now run smoothly :)
