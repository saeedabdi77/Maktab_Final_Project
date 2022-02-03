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






<p align="center">
    <img src="https://user-images.githubusercontent.com/90003082/152332517-011efb31-02ef-4c79-9bb0-ae72492833c8.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332528-6bbac134-82da-437e-acde-b31d9c28f5dc.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332557-69718678-3762-4524-be1c-b3ce9d5116fc.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332560-d473def6-8ede-47d0-a88c-589debaa3f92.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332566-8a774080-acfc-4307-813a-a5a75b35ede0.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332571-e0ed7cff-e1a0-443c-b1d9-f3e67af82f35.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332577-95883c7b-12ea-4934-846d-f2d29ddcbb7f.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332579-9eb5fe83-555a-417f-87eb-43bb983519db.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332580-f96f4574-c562-4c54-b71b-68b581a6b133.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332585-0318b1c9-1474-4a49-8f28-24f59399d693.png" width="400">
    <img src="https://user-images.githubusercontent.com/90003082/152332586-184c1f4b-d3c2-4fd6-9c83-073928c2f7d5.png" width="400">
</p>
