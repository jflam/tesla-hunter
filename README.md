# tesla-hunter

This is a python 3 script that queries the Tesla used inventory API. It was 
created based on the description of the Tesla inventory API contained in this 
[reddit post](https://www.reddit.com/r/TeslaLounge/comments/jwu5z0/having_fun_with_the_used_inventory_api_and_price/
).

The script will let you query for a car in the United States based on your
desired search criteria, e.g., exterior color, wheel size, type of drive, etc.

I wrote this script to look for a Model 3, so I haven't tried querying for 
the far more complicated option sets found in cars like the Model S. 

At the moment the script does not maintain a local pricing database. This
would be an interesting feature to add later, as it would let you know how 
close to a good "sold" price that you would get. It would be kind of like 
having a Zillow "zestimate" price for any given Model 3, given its model
year, mileage, and other computable features.

## colophon

It's worth noting that I wrote this entirely using the VS Code interactive
window experience. I had no idea how to use this API and there was a *lot*
of trial and error involved, which is a perfect scenario for using the
interactive window feature.