import pandas as pd
import json
import requests
import re
#Calling Sephora's API
url = "https://sephora.p.rapidapi.com/us/products/v2/list" 
# 60 bestsellers from the Skincare category
querystring = {"categoryId":"cat150006","pageSize":"60","currentPage":"1","sortBy":"P_BEST_SELLING:1"} 
headers = {
    "X-RapidAPI-Key": "ca26155aeemshc91293b842eea14p1488c3jsn69f7b43ca65c",
    "X-RapidAPI-Host": "sephora.p.rapidapi.com"
}
response = requests.get(url, headers=headers, params=querystring)
print(response.json()) #Output is JSON file
data = response.json()
# Printing the list of products
print(data['products'])

# Printing only product names
for product in data['products']:
    print(product['displayName'])
    
# Printing product IDs
for product in data['products']:
    print(product['productId'])

# making a list with product IDs
productIdList = []
for p in data['products']:
    productIdList.append(p['productId'])
print(productIdList)

# Collecting 60 reviews for each product
url = "https://sephora.p.rapidapi.com/reviews/list"
reviewList = []
for id in productIdList:
    querystring = {
        "ProductId": id,
        "Limit": "60",
        "Offset": "0"
    }
    headers = {
    "X-RapidAPI-Key": "4ece0ff090msh939a12667e0010dp1ca5b1jsn2da12519f0b9",
    "X-RapidAPI-Host": "sephora.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    reviewList.append(response.json())
with open("/Users/dascherry/Desktop/review_data.json", "w") as file:
    json.dump(reviewList, file) #Output is json file
print("Review data saved to review_data.json")

# Printing only the necessary information (id, name, review, whether it is incentivised or not, rating)
# from the json file in df
with open('/Users/dascherry/Desktop/review_data.json', 'r') as file:
    json_data = json.load(file)

# Loop through each element of the list
results_list = []
for element in json_data:
    results_data = element.get('Results', [])
    results_list.extend(results_data)

# Convert the 'Results' data into a DataFrame
df = pd.json_normalize(results_list)

# Extract 'IncentivisedReview' information from the nested dictionary
if 'ContextDataValues.IncentivizedReview.Value' in df.columns:
    df['Incentivised'] = df['ContextDataValues.IncentivizedReview.Value']
    
# Select only the desired columns
desired_columns = ["ProductId","OriginalProductName", "ReviewText", "Incentivised", "Rating"]
df = df[desired_columns]
# Saving the df as csv
df.to_csv('/Users/Dascherry/Desktop/sephora_data.csv', index=False)

# Some of the productIds don't start with P because they're different flavours/options
# for each product

# Filtering the rows where id doesn't start with P and printing product names
filtered_df = df[~df['ProductId'].str.startswith('P')]
print(filtered_df["OriginalProductName"])
filtered_df.to_csv('/Users/Dascherry/Desktop/filtered_df.csv', index=False)

# There are 17 products that have subproducts. 
# Using regex to define the beginning of product names and match them with corresponding P-ids
pattern = r'^(Lip Butter Balm|Lip Sleeping Mask Intense Hydration|Clean Face Mask|Lip Glowy Balm|Cleansing \+ Exfoliating|Clean Eye Mask|Glowmotions Glow Body|Lip Glow Oil|Dream Lip Oil|Balm Dotcom Lip|Lip Sleeping Mask|LipSoftie™ Hydrating|Fenty Treatz Hydrating|Lip Comfort Hydrating Oil|Honey Infused Hydrating Lip|Clean Lip Balm|Hydrating Face Mask).*'
matches = df['OriginalProductName'].str.extract(pattern)
new_filtered_df = df[matches.notnull().any(axis=1) & df['ProductId'].str.startswith('P')]
new_filtered_df[['OriginalProductName', 'ProductId']]
new_filtered_df.to_csv('/Users/Dascherry/Desktop/new_filtered_df.csv', index=False)

# Dropping duplicates to see the ids of the main products that will be assigned to the subproducts
new_filtered_df = new_filtered_df.drop_duplicates(subset=['ProductId'])
new_filtered_df[['OriginalProductName', 'ProductId']]

# Converting df to dictionary
product_dict = new_filtered_df.set_index('OriginalProductName')['ProductId'].to_dict()
product_dict

# Assigning main product ID to sub-products through the function by using the dictionary with the Ids

final_df = df
def assign_main_product_id(row):
    product_name = row['OriginalProductName']
    for beginning, main_product_id in product_dict.items():
        if product_name.startswith(beginning):
            return main_product_id
    # Return original product ID if no match found
    return row['ProductId']

# Apply the function to the DataFrame
final_df['ProductId'] = final_df.apply(assign_main_product_id, axis=1)
final_df

# Now all the products have P-Ids

# Some rows have NaN values 
# See the rows where Incentivised is NaN
rows_with_null = final_df[pd.isna(final_df['Incentivised'])]
rows_with_null

# Count NaN values for each 'MainProductId' in the 'Incentivised' column
null_counts = rows_with_null['Incentivised'].isna().groupby(rows_with_null['ProductId']).sum()

# Filter counts that are greater than 0
non_zero_null_counts = null_counts[null_counts > 0]

# Print 'MainProductId' for counts of NaN values greater than 0
if not non_zero_null_counts.empty:
    print(non_zero_null_counts)

null_counts_df = null_counts.reset_index()
null_counts_df.columns = ['ProductId', 'NaN_Count']

null_counts_df.to_csv('/Users/Dascherry/Desktop/null_counts.csv')

# Most of NaN values range from 1 to 14, so we're going just to drop those rows
# one product P465808 has 53 non defined reviews, so we'll exclude this product from the analysis

final_df2 = final_df[final_df['Incentivised'].notna() | (final_df['ProductId'] == 'P465808')]
final_df2

# Checking that there are no NaN values in the 'ProductId' column as well
nan_values = final_df2['ProductId'].isna().sum()
if nan_values > 0:
    print("There are NaN values in the 'ProductId' column.")
else:
    print("There are no NaN values in the 'ProductId' column.")
nan_rows = final_df2[final_df2['ProductId'].isna()]
print(nan_rows)

# Making separate df with average rating for each product

average_rating = final_df2.groupby('ProductId')['Rating'].mean().round(1)
average_rating_df = average_rating.reset_index()
average_rating_df.columns = ['ProductId', 'Average_Rating']
average_rating_df

# Converting 'Incentivised' column to boolean type to work with filtered reviews 
# (not including incentivised ones)
final_df3 = final_df2
final_df3['Incentivised'] = final_df3['Incentivised'].map({'True': True, 'False': False})

# Checking unique values in 'Incentivised' column
unique_values = final_df3['Incentivised'].unique()
# Checking the data type of 'Incentivised' column
incentivised_dtype = final_df3['Incentivised'].dtype
# Printing the results
print(unique_values)
print("Data type of 'Incentivised' column:", incentivised_dtype)

# Creating a new DataFrame where 'Incentivised' is not equal to True
final_df_filtered = final_df3[final_df3['Incentivised'] != True]

# Print the new DataFrame
print(final_df_filtered)

# Merge average_rating_df with the aggregated ratings from final_df_filtered
average_rating_df = average_rating_df.merge(final_df_filtered.groupby('ProductId')['Rating'].mean().reset_index().rename(columns={'Rating': 'Filtered_Rating'}), on='ProductId', how='left')

# Print the updated DataFrame
print(average_rating_df)
average_rating_df.to_csv('/Users/Dascherry/Desktop/average_rating_df.csv')

# Interactive pie chart to show changes in the rating 
import plotly.graph_objs as go
average_rating_df['rating_change'] = average_rating_df['Filtered_Rating'] - average_rating_df['Average_Rating']

# Counting changes 
no_change = (average_rating_df['rating_change'] == 0).sum()
lower_rating = (average_rating_df['rating_change'] < 0).sum()
higher_rating = (average_rating_df['rating_change'] > 0).sum()

# Labels and counts for visualisation 
labels = ['No Change', 'Lower Rating', 'Higher Rating']
counts = [no_change, lower_rating, higher_rating]

# Visualisation 
fig = go.Figure(data=[go.Pie(labels=labels, values=counts)])
fig.update_layout(title='Rating Change Comparison')
fig.show()

# The visualisation shows that if we didn't count incentivised reviews, the rating in most of the cases 
# the rating would remain the same. 

# Creating a new DataFrame where 'Incentivised' is equal to True
df_incentivised_reviews = final_df3[final_df3['Incentivised'] == True]
print(df_incentivised_reviews)

# What is the average rating of incentivised reviews?
incentivised_reviews_count = df_incentivised_reviews.groupby('ProductId').size().reset_index(name='Incentivised_Review_Count')
average_rating_incentivised = df_incentivised_reviews.groupby('ProductId')['Rating'].mean().round(1).reset_index()
average_rating_incentivised = average_rating_incentivised.merge(incentivised_reviews_count, on='ProductId')
average_rating_incentivised.columns = ['ProductId', 'Average_Rating','Incentivised_Review_Count']
average_rating_incentivised

# Making sentiment analysis of incentivised reviews using VADER
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

# Scoring each sentence
scores = []
for review in df_incentivised_reviews['ReviewText']:
    score = analyzer.polarity_scores(review)['compound']
    scores.append(score)
    
df_incentivised_reviews['sentiment_score'] = scores
print(df_incentivised_reviews)

# Visualisation to show how many reviews are positive, neutral or negative
import plotly.express as px

# Categorising positive, neutral and negative reviews
positive_threshold = 0.05
negative_threshold = -0.05

def sentiment(score):
    if score > positive_threshold:
        return 'Positive'
    elif score < negative_threshold:
        return 'Negative'
    else:
        return 'Neutral'
df_incentivised_reviews['sentiment_category'] = df_incentivised_reviews['sentiment_score'].apply(sentiment)
counts = df_incentivised_reviews['sentiment_category'].value_counts().reset_index()
counts.columns = ['Sentiment', 'Count']
print(counts)

# Creating a bar chart using Plotly
fig = px.bar(counts, x='Sentiment', y='Count', 
             color='Sentiment',
             color_discrete_map={'Positive': 'green', 'Negative': 'red', 'Neutral': 'gray'},
             title='Distribution of Sentiment in Reviews',
             labels={'Sentiment': 'Sentiment Category', 'Count': 'Number of Reviews'})
fig.show()

# Detailed analysis for P468658 as it has almost even number of incentivised and not reviews 

product_id = 'P468658'
product = final_df3[final_df3['ProductId'] == product_id]
product # innisfree's Super Volcanic Pore Clay Mask

# Average rating including and excluding incentivised reviews

name = "Super Volcanic AHA Pore Clearing Clay Mask"
reviews = final_df3[final_df3['OriginalProductName'] == name]
average_rating = reviews['Rating'].mean()
average_rating_filtered = reviews[reviews['Incentivised'] == False]['Rating'].mean()
print(average_rating)
print(average_rating_filtered )

# Sentiment analysis for all reviews
def sentiment_analysis(reviews):
    sentiment_score = analyzer.polarity_scores(review)
    return sentiment_score['compound']
reviews['Sentiment_score'] = reviews['ReviewText'].apply(sentiment_analysis)
sentiment_all_reviews = reviews['Sentiment_score'].mean()

# Sentiment analysis for filtered reviews
reviews_filtered = reviews.copy()
reviews_filtered['Sentiment_score'] = reviews[reviews['Incentivised'] == False]['ReviewText'].apply(sentiment_analysis)
sentiment_filtered = reviews_filtered['Sentiment_score'].mean()
print(sentiment_all_reviews)
print(sentiment_filtered)

# Making word cloud of filtered reviews


from wordcloud import WordCloud
import matplotlib.pyplot as plt

wordcloud_filtered = WordCloud(width=800, height=400, background_color='white').generate(' '.join(reviews_filtered['ReviewText']))
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud_filtered, interpolation='bilinear')
plt.title('Word Cloud for Reviews Excluding Incentivised')
plt.axis('off')
plt.show()

# Making word cloud of 10 most frequent key words in filtered reviews

wordcloud = WordCloud().generate(' '.join(reviews_filtered['ReviewText']))

# Extracting the words and their frequencies
word_freq = wordcloud.words_

# Sorting the words based on their frequencies
sorted_word_freq = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

# Selecting the top 10 keywords
top_10_keywords = sorted_word_freq[:10]

for keyword, freq in top_10_keywords:
    print(f"{keyword}: {freq}")

plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
