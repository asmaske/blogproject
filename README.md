# Blog project

Blog project is a Python based web project to maintain blog posts.

### Running the application on Google App Engine (Cloud)
1. The application is available on google app engine
2. The application has following features:
 + View blogs listing
 + Create a new blog
 + View a blog's owner, content, likes, unlikes and comments
 + Owner can edit a blog
 + Owner can delete a blog
 + Viewer can like / unlike a blog
 + Viewer can comment on a blog
 + Author of a comment can edit/delete a comment
2. Open **https://ash-blogproject.appspot.com/blog** in the web browser
3. Click signup to create account
4. **https://ash-blogproject.appspot.com/blog** 
display all the blogs
5. **https://ash-blogproject.appspot.com/blog/newpost**
create a new blog
6. **https://ash-blogproject.appspot.com/blog/blogid**
display blog content, owner, likes count, unlikes count and comments
example: https://ash-blogproject.appspot.com/blog/1
7. **https://ash-blogproject.appspot.com/blog/editpost/blogid**
edit an existing blog
only owner of a blog can edit blog
example:
https://ash-blogproject.appspot.com/blog/editpost/1
8. **https://ash-blogproject.appspot.com/blog/commentpost/blogid**
add a comment to a blog
owner of a blog cannot add a comment to self blog
example:
https://ash-blogproject.appspot.com/blog/commentpost/1
9. **https://ash-blogproject.appspot.com/blog/likeunlikepost/blogid**
**like** or **unlike** an existing blog
owner of a blog cannot **like/unlike** blog
example:
https://ash-blogproject.appspot.com/blog/likeunlikepost/1
10. **https://ash-blogproject.appspot.com/blog/editdeletecomment/commentid**
edit or delete an existing comment
only author who created the comment can edit or delete comment
example:
https://ash-blogproject.appspot.com/blog/editdeletecomment/1
11. **https://ash-blogproject.appspot.com/blog/deletepost/blogid**
delete an existing blog
only owner of a blog can delete blog
example:
https://ash-blogproject.appspot.com/blog/deletepost/1

#### Note

 - Because sometime updates are cached, the change may not be visible. Press refresh button to see the changes. 
 - Test data created with two users
 - Some message and errors are reported on a separate page

### Tech

Portfolio Website uses the following software:

* [Python](https://www.python.org/) - Programming Language
* [Google App Engine](https://cloud.google.com/appengine/) - Platform to build software apps

## Project Details

### Running the application with Google App Engine (Local machine)
#### 1. Python
+ Download and install the stable version of **Python 2.7**
+ Add Python executables location to the PATH environment variable.
#### 2. Google App Engine
+ Download and install the App Engine SDK for Python from **https://cloud.google.com/appengine/docs/python/download**
#### 3. BlogProject application
+ Clone/copy the **BlogProject** source files to a local directory
#### 4. Running the application
+ Launch Google App Engine by running **install_location\google_appengine\launcher\GoogleAppEngineLauncher.exe**
+ Under **File** menu option select **Select Add Existing Application**
+ In **Application Path**, browse to the location of **BlogProject** directory and click **Add**
+ On the launcher, select project name and click **Run**
+ Click the **Browse** icon to launch the app in the browser
+ To view blogs, type **http://localhost:8080/blog**
#### 3. Application Directory Structure
* BlogProject
    + README.md
    + blog.py
    + index.yaml
    + app.yaml
    + static
	    + main.css
    + templates
	    + base.html
	    + front.html
	    + signup-form.html
	    + login-form.html
	    + post.html
	    + permalink.html
	    + newpost.html
	    + editpost.html
	    + deletepost.html
	    + editdeletecomment.html
	    + likeunlikepost.html
	    + errorpost.html
	    + messagepost.html