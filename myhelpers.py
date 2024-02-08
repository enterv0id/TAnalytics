import pandas as pd

cols_to_drop = ['BAInfo','adAuthorization','adLabelVersion','aigcLabelType','aigcLabelType','anchors','author_avatarLarger','author_avatarThumb','author_commentSetting','author_downloadSetting','author_duetSetting','author_ftc','author_isADVirtual','author_isEmbedBanned','author_openFavorite','author_privateAccount','author_relation','author_roomId','author_secUid','author_secret','author_stitchSetting','author_ttSeller','collected','contents_0_textExtra','digged','duetDisplay','duetEnabled','duetInfo','forFriend','itemCommentStatus','itemMute','music_coverLarge','music_coverThumb','officalItem','playlistId','privateItem','secret','shareEnabled','showNotPass','stitchDisplay','stitchEnabled','textExtra','video_bitrateInfo','video_codecType','video_encodeUserTag','video_encodedType','video_format','video_shareCover','video_subtitleInfos','video_videoQuality','video_volumeInfo','video_zoomCover','videoSuggestWordsList','vl1','challenges','stickersOnItem','video_bitrate','contents_1_desc','contents_1_textExtra','contents_2_desc','contents_3_desc','contents_4_desc','contents_4_textExtra','effectStickers','contents_2_textExtra','contents_3_textExtra','poi_category','poi_city','poi_cityCode','poi_country','poi_countryCode','poi_fatherPoiId','poi_fatherPoiName','poi_id','poi_name','poi_province','poi_ttTypeCode','poi_ttTypeNameMedium','poi_ttTypeNameSuper','poi_ttTypeNameTiny','poi_type','poi_typeCode']
old_names = ['Date','Video_link','desc','stats_diggCount','stats_commentCount','stats_collectCount','authorStats_followerCount','authorStats_heart','stats_playCount','authorStats_videoCount','video_duration','video_ratio','video_dynamicCover']
new_names = ['Date','Video Link','Description','Likes','Comments','Shares','Followers','Hearts','Plays','Videos','Video duration','Video quality','Video Thumbnail']

def process_results(data):
    nested_values = ["authorStats", 'author', "contents", "stats", "music",'video','poi']
    skip_values = ['challenges',"duetInfo","textExtra","bitrateInfo","shareCover","volumeInfo","zoomCover"]

    # Create blank dictionary
    flattened_data = {}
    # Loop through each video
    for idx, value in enumerate(data):
        flattened_data[idx] = {}
        # Loop through each property in each video
        for prop_idx, prop_value in value.items():
            # Check if nested
            if prop_idx in nested_values:
                if prop_idx in skip_values:
                    pass
                else:
                    # Check if prop_value is a dictionary
                    if isinstance(prop_value, dict):
                        # Loop through each nested property
                        for nested_idx, nested_value in prop_value.items():
                            flattened_data[idx][prop_idx+'_'+nested_idx] = nested_value
                    # Check if prop_value is a list
                    elif isinstance(prop_value, list):
                        # Loop through each item in the list
                        for i, item in enumerate(prop_value):
                            # Check if the item is a dictionary
                            if isinstance(item, dict):
                                # Loop through each property in the dictionary
                                for nested_idx, nested_value in item.items():
                                    flattened_data[idx][prop_idx+'_'+str(i)+'_'+nested_idx] = nested_value
            # If it's not nested, add it back to the flattened dictionary
            else:
                flattened_data[idx][prop_idx] = prop_value

    return flattened_data

def convert_to_datetime(df, col='createTime'):
    '''
    Convert unix timestamp to datetime
    :param df:
    :param col:
    :return:df['hour'],df['day']
    '''
    df[col] = pd.to_datetime(df[col], unit='s')
    df['Date'] = df[col].dt.date
    df['hour'] = df[col].dt.hour
    df['day'] = df[col].dt.dayofweek+1
    return df


def drop_cols(df):
    for col in cols_to_drop:
        if col in df.columns:
            df = df.drop(col, axis=1)
    return df

def make_vid_url_col(df):
    df['Video_link'] = 'https://www.tiktok.com/@'+df['author_uniqueId']+'/video/'+df['video_id'].astype(str)
    return df


def rename_and_reorder(df):
    # Create a mapping of old names to new names
    name_mapping = dict(zip(old_names, new_names))

    # Rename the columns
    df = df.rename(columns=name_mapping)

    # Get the remaining columns that were not reordered
    remaining_cols = [col for col in df.columns if col not in new_names]

    # Create the new order of columns
    new_order = new_names + remaining_cols

    # Reorder the columns
    df = df.reindex(columns=new_order)

    return df