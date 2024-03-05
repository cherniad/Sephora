# Sephora

 __Introduction__ 

 The purpose of this project is, to analyze whether incentivised reviews for products on Sephora website change the actual rating of the products or not. 
 The sentiment analysis will be also performed on the reviews. 

 
__Libraries used:__
- pandas
- json
- re
- requests
- plotly
- VaderSentiment
- wordcloud
- matplotlib

__Additional Sources__

_API:_
https://rapidapi.com/apidojo/api/sephora

__Steps:__

1. Call the API and collect the information about 60 products

2. Make the list with product IDs and use it to call the api and collect 60 reviews for each product

   * The output can be consulted in review_data.json

3. Create a dataframe with the following information: Product Id, Product Name, Review Text, Incentivised Review or not, Rating
   from the data collected in (1) and (2).
   
4. Process the data:

    a) Make sure that all the products have consistent IDs starting with letter 'P', as some have subproduct IDs that are numeric.
        For example, the product "Lip Butter Balm for Hydration & Shine" have such subroducts as "Lip Butter Balm for Hydration & Shine Birthday Cake",
        "Lip Butter Balm for Hydration & Shine Vanilla Beige", "Lip Butter Balm for Hydration & Shine Brown Sugar" etc.
        Use regex to assign main product IDs to all the subproducts.
   
     b) Drop the rows that contain NaN values in the Incentivised column
   
     c) One product had 53 NaN values in the Incentivised column, hence exclude the product from the analysis

6. Make a separate dataframe with average rating for each product

7. Convert 'Incentivised' column to boolean type to work with filtered reviews 

8. Calculate average rating for filtered reviews that exclude incentivised reviews

9. Make interactive pie chart to show changes in the rating before and after incentivised reviews
![1](https://github.com/cherniad/Sephora/assets/129260187/4c71c1e4-01e3-48e7-8d06-444b1349634a)

10. Calculate the average rating of incentivised reviews

11. Make sentiment analysis of incentivised reviews using VADER

12. Make a visualisation to show how many incentivised reviews are positive, neutral or negative
![2](https://github.com/cherniad/Sephora/assets/129260187/b4bcee85-d7aa-4699-a6ab-bbf8f97c4308)

13. Make a detailed analysis of individual product (I have chosen the one where the ratio of incentivised/non-incentivised reviews was around 50/50):
    
    a) Calculate average rating including and excluding incentivised reviews
    b) Make sentiment analysis for all reviews
    c) Make sentiment analysis for filtered reviews
    d) Make word cloud of filtered reviews
    ![Unknown-2](https://github.com/cherniad/Sephora/assets/129260187/9f84f03f-1387-4e87-a938-98328669c550)

    e) Make word cloud of 10 most frequent key words in filtered reviews

    ![Unknown-4](https://github.com/cherniad/Sephora/assets/129260187/b55d1359-8a93-406f-86a2-a2379501a1b8)




__Results and Learning Outcomes__ 

The code could be used for a manufacturing companies and marketing departments to assess product performance and gather non-incentivised feedback. The analysis revealed that sometimes incentivised reviews can even lower the actual rating of the product, although they are usually positive. The individual product analysis showed no significant differences in the most frequent key words in filtered and non-filtered reviews, however, it might not be the case for each product. In the future, it is possible also to tailor a specific lexicon database containing terms for skincare products reviews as VADER provides more general sentiment labeling.
 

