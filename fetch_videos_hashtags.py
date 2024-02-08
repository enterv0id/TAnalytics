
from TikTokApi import TikTokApi
import asyncio
import os
from myhelpers import process_results,drop_cols,make_vid_url_col,convert_to_datetime,rename_and_reorder
import pandas as pd
import sys
import tempfile

mstoken = "7F0KrTw00Idsz41y1iQ0FJTbv0ECuPP8YB8kQscBQjw884QDlu7lUJeCxU32SLoDLRFt0_wRghu_KwSF-oKRDulKq97MN1xNg_OpAae2ubMeX4yQfR_Yd94bNjZdsfb53q5lUJcqGN1pZETDSg=="
ms_token = os.environ.get(mstoken, None)  # set your own ms_token

# number_of_videos = 20
# hashtag = "dogsoftiktok"
async def get_hashtag_videos(number_of_videos, hashtag):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3,headless=False)
        tag = api.hashtag(name=hashtag)
        videos = []
        async for video in tag.videos(count=number_of_videos):
            videos.append(video.as_dict)
            # if len(videos) >= number_of_videos:
            #     break
        flattened_data = process_results(videos)
        df = pd.DataFrame.from_dict(flattened_data, orient='index')
        df = drop_cols(df)
        df = convert_to_datetime(df)
        df = make_vid_url_col(df)
        df = rename_and_reorder(df)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
            df.to_csv(temp.name, index=False)
            print(temp.name)
        # df.to_csv('vids_from_hashtags.csv', index=False)

if __name__ == "__main__":
    # print(sys.argv[1], sys.argv[2])
    asyncio.run(get_hashtag_videos(int(sys.argv[1]), sys.argv[2]))
