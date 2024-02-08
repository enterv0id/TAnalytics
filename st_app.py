import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import pandas as pd
from wordcloud import WordCloud, STOPWORDS
import nltk
from collections import Counter
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE
@st.cache_data
def load_data(path: str):
    data = pd.read_csv(path)
    return data
nltk.download('punkt')
def get_temp_file_path(script, *args):
    process = Popen(["python", script] + list(args), stdout=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    return output.decode('utf-8').strip()

def create_heatmap(df, left_column):
    heatmap_data = df.groupby(['hour', 'day']).size().reset_index(name='count')
    heatmap_data = heatmap_data.pivot(index='hour', columns='day', values='count')

    plt.figure(figsize=(10, 10))  # Adjust the size of the figure. You can change the values as needed.

    sns.heatmap(heatmap_data, annot=True, vmin=0, vmax=heatmap_data.max().max())
    plt.title('Heatmap of Video Posting Times')
    plt.xlabel('Day of the Week(1=Monday, 7=Sunday)')
    plt.ylabel('Hour of the Day')
    left_column.pyplot(plt.gcf(), use_container_width=True)

def create_scatter_plot(df, x, y, right_column):
    if x in df.columns and y in df.columns:  # Ensure x and y columns exist in the DataFrame
        fig = go.Figure(data=go.Scatter(
            x=df[x],
            y=df[y],
            mode='markers',
            hovertemplate=
            '<i>Author</i>: %{customdata[8]}' +
            '<br><b>Plays</b>: %{y}<br>' +
            '<b>Likes</b>: %{customdata[0]}' +
            '<br><b>Comments</b>: %{customdata[1]}' +
            '<br><b>Shares</b>: %{customdata[2]}' +
            '<br><b>Followers</b>: %{customdata[3]}' +
            '<br><b>Videos</b>: %{customdata[4]}' +
            '<br><b>Video Duration</b>: %{customdata[5]}' +
            '<br><b>Video Quality</b>: %{customdata[6]}' +
            '<br><b>Author Verification</b>: %{customdata[7]}',
            customdata=df[['Likes', 'Comments', 'Shares', 'Followers', 'Videos', 'Video duration', 'Video quality',
                           'author_verified','author_uniqueId']].values
        ))
        fig.update_layout(
            title='Relationship between ' + x + ' and ' + y,
            xaxis_title=x,
            yaxis_title=y,
            autosize=True,
        )
        right_column.plotly_chart(fig, use_container_width=True)
def create_word_cloud(df, left_column):
    hashtags = df['Description'].str.cat(sep=' ')
    wordcloud = WordCloud(stopwords=STOPWORDS, width=800, height=800, max_font_size=120,
                          background_color='white').generate(hashtags)
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    left_column.pyplot(plt)

def create_word_frequency_histogram(df, right_column):
    hashtags_no_hash = df['Description'].str.replace('#', '')
    words = hashtags_no_hash.str.split(expand=True).stack()
    filtered_words = [word for word in words if word not in STOPWORDS]
    word_counts = Counter(filtered_words)
    df_words = pd.DataFrame.from_dict(word_counts, orient='index').reset_index()
    df_words.columns = ['Word', 'Frequency']
    df_words = df_words.sort_values(by='Frequency', ascending=False)
    fig = px.bar(df_words.head(20), x='Word', y='Frequency',
                 labels={'Word': 'Words', 'Frequency': 'Frequency'},
                 title='Word Frequency Histogram')
    fig.update_layout(autosize=True)
    fig.update_xaxes(tickangle=45, tickfont=dict(size=14))
    fig.update_yaxes(tickfont=dict(size=14))
    right_column.plotly_chart(fig, use_container_width=True)

def create_bar_chart(df, right_column, num_authors):
    # Select the top num_authors authors based on the 'Plays' column
    top_authors_df = df.nlargest(num_authors, 'Plays')

    fig = go.Figure(data=go.Bar(
        x=top_authors_df['author_uniqueId'],
        y=top_authors_df['Plays'],
        hovertemplate=
        '<i>Author</i>: %{x}' +
        '<br><b>Plays</b>: %{y}<br>' +
        '<b>Likes</b>: %{customdata[0]}' +
        '<br><b>Comments</b>: %{customdata[1]}' +
        '<br><b>Shares</b>: %{customdata[2]}' +
        '<br><b>Followers</b>: %{customdata[3]}' +
        '<br><b>Videos</b>: %{customdata[4]}' +
        '<br><b>Video Duration</b>: %{customdata[5]}' +
        '<br><b>Video Quality</b>: %{customdata[6]}' +
        '<br><b>Author Verification</b>: %{customdata[7]}',
        customdata=top_authors_df[['Likes', 'Comments', 'Shares', 'Followers', 'Videos', 'Video duration', 'Video quality',
                       'author_verified']].values
    ))

    fig.update_layout(
        title='Plays by Top ' + str(num_authors) + ' Authors',
        xaxis_title='Author',
        yaxis_title='Plays',
        autosize=True,
    )
    right_column.plotly_chart(fig, use_container_width=True)

plt.rcParams['font.family'] = 'Arial'
st.set_page_config(layout='wide')
st.title("TikTok Analytics")
st.sidebar.markdown("<div><img src='https://iconape.com/wp-content/files/pu/380444/svg/380444.png' width=200 /><h1 style='display:inline-block'>Tiktok Analytics</h1></div>", unsafe_allow_html=True)



if 'layout' not in st.session_state:
    st.session_state['layout'] = 'Get Trending Videos'
st.session_state['layout'] = st.sidebar.selectbox('Please choose the needed service:', ('Get Videos from Hashtags','Get Trending Videos'))


if st.session_state['layout'] == 'Get Videos from Hashtags':
    st.sidebar.markdown(
        "To get started <ol><li>Enter the <i>hashtag</i> you wish to analyse</li> <li>Hit <i>Get Data</i>.</li> <li>Get analyzing</li></ol>",
        unsafe_allow_html=True)
    hashtag = st.text_input('Search for a hashtag here:', value="catsoftiktok")
    number_of_videos = st.number_input('Number of videos to return:', value=100)


    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()

    if st.button("Get Data"):
        message = st.empty()
        message.write("Searching for videos with the hashtag: " + hashtag)
        # call(["python", "fetch_videos_hashtags.py", str(number_of_videos), hashtag])
        temp_file_path = get_temp_file_path("fetch_videos_hashtags.py", str(number_of_videos), hashtag)
        st.session_state['df'] = load_data(temp_file_path)
        message.empty()
        st.write("Done")

    if not st.session_state['df'].empty:
        left_column, right_column = st.columns(2)
        if st.session_state['layout'] == 'Get Videos from Hashtags':
            create_heatmap(st.session_state['df'], left_column)
            create_word_cloud(st.session_state['df'], left_column)
            column_names = ['Likes', 'Comments', 'Shares', 'Plays', 'Followers', 'Videos', 'Hearts', 'Video duration',
                            'Video quality']

            if 'x_column' not in st.session_state:
                st.session_state['x_column'] = column_names[0]
            if 'y_column' not in st.session_state:
                st.session_state['y_column'] = column_names[1]

            x = right_column.selectbox('Select x column:', column_names, key='x_column')
            y = right_column.selectbox('Select y column:', column_names, key='y_column')

            if st.session_state['x_column'] != x or st.session_state['y_column'] != y:
                st.session_state['x_column'] = x
                st.session_state['y_column'] = y
            else:
                create_scatter_plot(st.session_state['df'], x, y, right_column)


            create_word_frequency_histogram(st.session_state['df'], right_column)

            with st.expander('Data Preview'):
                st.data_editor(st.session_state['df'], column_config={
                    "Video Link": st.column_config.LinkColumn(
                        label='Video Link',
                        help="Open video link")},
                               hide_index=True,
                               )

elif st.session_state['layout'] == 'Get Trending Videos':
    if 'df' in st.session_state:
        del st.session_state['df']
    st.sidebar.markdown(
        "To get started <ol><li>Enter the <i>Number of videos</i> you wish to analyze</li> <li>Hit <i>Get Data</i>.</li> <li>Get analyzing</li></ol>",
        unsafe_allow_html=True)
    number_of_videos = st.number_input('Number of videos to return:', value=20)
    if 'df' not in st.session_state:
        st.session_state['df'] = pd.DataFrame()

    if st.button("Get Data"):
        message = st.empty()
        message.write("Getting the trending videos... ")
        # call(["python", "fetch_trending_vids.py", str(number_of_videos)])
        temp_file_path = get_temp_file_path("fetch_trending_vids.py", str(number_of_videos))
        st.session_state['df'] = load_data(temp_file_path)
        message.empty()
        st.write("Done")

    if not st.session_state['df'].empty:
        left_column, right_column = st.columns(2)

        create_heatmap(st.session_state['df'], left_column)
        create_word_cloud(st.session_state['df'], left_column)
        create_bar_chart(st.session_state['df'], right_column,10)

        create_word_frequency_histogram(st.session_state['df'], right_column)

        with st.expander('Data Preview'):
            st.data_editor(st.session_state['df'], column_config={
                "Video Link": st.column_config.LinkColumn(
                    label='Video Link',
                    help="Open video link")},
                           hide_index=True,
                           )