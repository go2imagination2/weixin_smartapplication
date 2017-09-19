


# About nginx serving static file

## include vhost config file in the main nginx conf file for subdomin


vi /usr/local/nginx/conf/nginx.conf
vi /usr/local/nginx/conf/vhost/exam.uperform.cn.conf


## static file folder should NOT put in /root
set the owner to www or root if necessary 
set permission to 755 or 644

## perfer to use 'alias' in nginx conf

`root` will append the URI into to the file path, while `alias` not

## Add DNS parsing for subdomin name



