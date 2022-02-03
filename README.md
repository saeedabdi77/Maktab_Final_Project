# OnlineStore Django web Application
## Features
This web application contains:

* login / logout :
     * login with email/phone_number and password
     * login with email/phoene_number and otp (send otp via sms) (phone number must be verifeid)
     * session based login for sellers
     * token based login for buyers

* forget password with receive email

* swagger customized

* customized admin:
    * search feild
    * filter
    * ediatable feild
    * change status action
    * show image in admin panel
    * ...

* seller (django template):
    * only sellers can access
    * add/edit/delete store
    * can have multiple stores but one processing at a time
    * add/edit product for each store
    * products can have multiple images and one as default
    * while seller add a new product must fill in some extra feilds depend on product type
    * can see all orders (filter on orders based on status or timestamp)
    * can see order detail
    * can change order status (buyer receives email when order status is changed)
    * can see customers reports
    * can see store sold products reports (used charts)
    * ...
    
* buyer (django-rest):
    * api for:
      * register
      * put/get profile
      * access/refresh token
      * verify phone number
      * receive otp
      * get store types
      * get confirmed stores (can filter on store tpes)
      * get buyable products based on store (filter on price and product type)
      * post/get/delete cart (buyer can only have one active cart at a time)
      * post/put/delete cart item
      * get previous orders
      * ...
      
* blog (forum):
    * all users can post their photos
    * delete/update post
    * draft/published posts (other users can only see published posts)
    * each user can like and dislike a post only once
    * users comment and reply comment
    * each user has a profile
    * serach on title and caption
    * category
    * tag
    * users can add/delete/edit categories or tags
    * user can change profile photo
    * change password
    * contact us
    * ...
    
## Technologies
  * Python
  * Django
  * Django-Rest
  * JQuery
  * HTML
  * CSS
  * Bootstrap
  * Javascript

## Here are some pages of This Project

