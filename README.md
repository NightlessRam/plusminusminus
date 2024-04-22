# CSE 312 Web Project Link :  [https://200-not-ok.me](https://200-not-ok.me)
### Group name: 200 OK
### Group members:
1. "ThisIsDiff" ubit: chongzep
2. "gittoit" ubit: tlee47
3. "ChrisChen1771" ubit: ychen379
4. "xXColinWongXx" ubit: Colinwon
5. "NightlessRam" ubit: guoweixu

# Overview 
We are designing the backend of a social media web app where users can upload food reviews and connect with one another to show each other the new restaurants, bars, cafes, or food courts they discover. Users can currently post and interact with other posts, but we will have more interactive features on the way!

#  WalkThrough 
[1) Register an Account](#register-an-account-with-us)

[2) Create a Post](#create-a-post-to-share-with-others)

[3) Interact with other Posts](#create-a-post-to-share-with-others)

[4) Send a Direct Message to other Users](#sending-a-dm)


## Preview As a Guest & Click the Image Button
 <img width="1404" alt="Screenshot 2024-04-22 at 08 17 27" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/032070f3-7c24-420d-8233-71b252c40c32">
<img width="1417" alt="Screenshot 2024-04-22 at 08 18 19" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/681701e1-4bb3-4b9d-ad62-19a5560cd805">

## Register an Account With Us
<img width="1420" alt="Screenshot 2024-04-22 at 08 19 16" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/0f8f34b2-1fe6-4e22-9ea2-fc162709ff2d">
 <strong>Make Sure to remember your PASSWORD, as we have no support for password recovery right now! </strong> 

## Login with the Credentials 
<img width="1418" alt="Screenshot 2024-04-22 at 08 21 03" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/982ff480-e143-446d-9bb4-d63ba4d81281">

## Once logged in, the username registered with your account is displayed at the top 
<img width="1423" alt="Screenshot 2024-04-22 at 08 22 09" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/4ea195b2-04ba-4614-826d-3800eb29d988">

## Create a Post to Share with Others
<strong>Write your message! (This gets sent using polling)</strong> 
<img width="1412" alt="Screenshot 2024-04-22 at 08 26 28" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/9dec33e1-bf78-4fe9-9837-e9cc7d4adcb8">
<strong>Scroll to the bottom to find your latest post!</strong>
<img width="1413" alt="Screenshot 2024-04-22 at 08 26 44" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/287eaa5f-9972-429f-8a57-57336f6a60e3">

## Userlist
<strong>Logged in users and connected to websocket will appear on the bottom-right!</strong>
<strong>Just Like the Homework 4 LO3 and AO1, where user will disappear when closing browser/logout</strong>

## Sending a DM
<strong>Find a user to message from the user list on the bottom-right!</strong>
<img width="1401" alt="Screenshot 2024-04-22 at 08 23 00" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/6e53db2b-09ac-4ebc-ac0c-7c04fae35e9c">
<strong>Write your message!</strong> 
<img width="1419" alt="Screenshot 2024-04-22 at 08 23 35" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/d177121f-9a86-4100-aab3-96faaa08f649">
<strong>Then it gets sent over using WebSockets, and other users won't be able to see your direct message!</strong> 
<img width="1423" alt="Screenshot 2024-04-22 at 08 24 02" src="https://github.com/NightlessRam/plusminusminus/assets/109171773/ab82100b-0de6-4097-848c-8887f18b8f8a">

## Sources

https://flask-pymongo.readthedocs.io/en/latest/

https://flask.palletsprojects.com/en/2.3.x/quickstart/

https://www.fullstackpython.com/flask-templating-render-template-examples.html

https://www.geeksforgeeks.org/python-os-environ-object/

https://www.freecodecamp.org/news/how-to-use-fetch-api/


