from TikTokApi import TikTokApi
import asyncio
import os
from myhelpers import process_results,drop_cols,make_vid_url_col,convert_to_datetime,rename_and_reorder
import pandas as pd
import sys
import tempfile

mstoken = "7F0KrTw00Idsz41y1iQ0FJTbv0ECuPP8YB8kQscBQjw884QDlu7lUJeCxU32SLoDLRFt0_wRghu_KwSF-oKRDulKq97MN1xNg_OpAae2ubMeX4yQfR_Yd94bNjZdsfb53q5lUJcqGN1pZETDSg=="
ms_token = os.environ.get(mstoken, None)  # set your own ms_token

# number_of_videos= 20
async def trending_videos(number_of_videos):
    async with TikTokApi() as api:
        await api.create_sessions(ms_tokens=[ms_token], num_sessions=1, sleep_after=3,headless=False)
        videos = []
        async for video in api.trending.videos(count=number_of_videos):
            # print(video.as_dict)
            videos.append(video.as_dict)
            if len(videos) >= number_of_videos:
                break
        flattened_data = process_results(videos)
        df = pd.DataFrame.from_dict(flattened_data, orient='index')
        df = drop_cols(df)
        df = convert_to_datetime(df)
        df = make_vid_url_col(df)
        df = rename_and_reorder(df)
        df.sort_values(by='Plays', ascending=False, inplace=True)
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
            df.to_csv(temp.name, index=False)
            print(temp.name)
        # df.to_csv('trending_vids.csv', index=False)

if __name__ == "__main__":
    asyncio.run(trending_videos(int(sys.argv[1])))