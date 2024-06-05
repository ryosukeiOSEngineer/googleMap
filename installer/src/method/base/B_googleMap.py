# coding: utf-8
# ----------------------------------------------------------------------------------
# 2023/5/8更新

# ----------------------------------------------------------------------------------

import time
import requests
import const
import json
import pandas as pd
from dotenv import load_dotenv

# 自作モジュール
from .utils import Logger, NoneChecker

load_dotenv()

###############################################################
# googleMapApiを使ってrequest

class GoogleMapBase:
    def __init__(self, api_key, debug_mode=False):
        self.api_key = api_key

        # logger
        self.setup_logger = Logger(__name__, debug_mode=debug_mode)
        self.logger = self.setup_logger.setup_logger()

        # noneチェック
        self.none = NoneChecker()


###############################################################
# ----------------------------------------------------------------------------------
# Google mapAPIへのrequest

    def _google_map_api_request(self, query):
        try:
            self.logger.info(f"******** google_map_api_request 開始 ********")

            self.logger.debug(f"query: {query}")

            endpoint_url = const.endpoint_url

            params = {
                'query' : query,  # 検索ワード
                'key' : self.api_key
            }

            response = requests.get(endpoint_url, params=params, timeout=10)

            # self.logger.info(f"response: {response[:20]}")


            if response.status_code == 200:
                json_data = response.json()
                self.logger.info(f"リクエスト成功: {json_data}")
                return json_data

            elif response.status_code == 500:
                self.logger.error(f"google_map_api_request サーバーエラー")
                raise Exception("サーバーエラー")

            else:
                self.logger.error(f"google_map_api_request リクエストした際にエラーが発生: {response.status_code} - {response.text}")
                raise Exception("リクエストした際にエラーが発生")


        except requests.exceptions.Timeout:
            self.logger.error(f"google_map_api_request リクエストでのタイムアウトエラー")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"google_map_api_request リクエストエラーが発生: {e}")

        except Exception as e:
            self.logger.error(f"google_map_api_request 処理中にエラーが発生: {e}")

        finally:
            self.logger.info(f"******** google_map_api_request 終了 ********")

        return None


# ----------------------------------------------------------------------------------
# jsonファイルの全ての中身を確認

    def _response_result_checker(self, json_data):
        try:
            self.logger.info(f"******** response_result_checker 開始 ********")

            if json_data:
                self.logger.warning(json.dumps(json_data, indent=2, ensure_ascii=False))

            else:
                raise Exception("json_data データがなし")

            self.logger.info(f"******** response_result_checker 終了 ********")


        except Exception as e:
            self.logger.error(f"response_result_checker 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# 取得したjsonデータを再リクエストしなくて済むようにデータに置き換える


    def _get_json_to_dataframe(self, json_data):
        try:
            self.logger.info(f"******** _get_json_to_dataframe 開始 ********")

            # json_dataの中身を確認
            self._response_result_checker(json_data=json_data)

            # json_dataの「results」部分を抜き出す
            # places = json_data.get('results', [])

            # jsonデータをDataFrameに変換
            df = pd.json_normalize(json_data)

            self.logger.debug(df.head())

            # DataFrameをデバッグ用にCSV出力
            df.to_csv('installer/result_output/res_df.csv')

            return df

        except Exception as e:
            self.logger.error(f"_get_json_to_dataframe 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# DataFrameから複数のcolumnの値データを取得する
#! columnsで必要なcolumnを順番に指定する
#! →columns = ["name", "geometry.location.lat", "geometry.location.lng", "rating"]

    def get_column_data_in_df(self, df, columns):
        try:
            self.logger.info(f"******** get_column_data_in_df 開始 ********")

            store_data_list = []

            if df:
                # iterrowsは一つずつ取り出す→Indexとデータをタプルで返す
                for index, row in df.iterrows():
                    # rowのデータからcolumnのデータをリストに入れ込んでいく
                    store_data = {column: row[column] for column in columns}

                    self.logger.info(f"store_data: {index} {store_data}")

                    store_data_list.append(store_data)

            else:
                self.logger.error(f"dfがNoneになっている")

            self.logger.warning(f"store_data_list: \n{store_data_list}")

            self.logger.info(f"******** get_column_data_in_df 終了 ********")

            return store_data_list

        except Exception as e:
            self.logger.error(f"get_column_data_in_df 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# jsonファイルの特定のcolumnの内容を確認

    def _get_json_column_only_data(self, json_data, column):
        try:
            self.logger.info(f"******** _json_column 開始 ********")

            self.logger.debug(f"column:{column}")

            # jsonファイルが存在確認
            if not json_data:
                raise ValueError("json_data がNoneです")

            # jsonファイルに指定したcolumnがあるのか確認
            if column in json_data:
                raise KeyError(f"column '{column}' が JSONデータに存在しません")

            # jsonファイルの中にある'results'の中からデータを抜く
            places = json_data.get('results', [])

            for place in places:

                # columnごとの値
                column_value = place.get(column)

            self.logger.warning(f"column_value: {column_value}")

            self.logger.info(f"******** _json_column 終了 ********")

            return column_value


        except KeyError as ke:
            self.logger.error(f"指定されたカラムにエラーがあります: {ke}")

        except ValueError as ve:
            self.logger.error(f"指定したcolumnのデータが指定したJSONファイルにない: {ve}")

        except Exception as e:
            self.logger.error(f"response_result_checker 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# jsonファイルの特定の階層がある部分の値を取得

    def _get_json_column_hierarchy_data(self, json_data, column, column2, column3):
        try:
            self.logger.info(f"******** response_result_checker 開始 ********")

            self.logger.debug(f"columns: {column}, {column2}, {column3}")

            if not json_data:
                raise ValueError("json_data がNoneです")


            # jsonファイルの中にある'results'の中からデータを抜く
            places = json_data.get('results', [])

            for place in places:
                if column in place and column2 in place[column] and column3 in place[column][column2]:

                # columnごとの値
                    column_value = place[column][column2][column3]

                else:
                    raise KeyError(f"指定したcolumn '{column}/{column2}/{column3}'が jsonデータに存在しない")

            self.logger.warning(f"column_value: {column_value}")

            self.logger.info(f"******** response_result_checker 終了 ********")

            return column_value


        except KeyError as ke:
            self.logger.error(f"指定されたカラムにエラーがあります: {ke}")

        except ValueError as ve:
            self.logger.error(f"指定したcolumnのデータが指定したJSONファイルにない: {ve}")

        except Exception as e:
            self.logger.error(f"response_result_checker 処理中にエラーが発生: {e}")

# ----------------------------------------------------------------------------------
# place_idを取得

    def _get_place_id(self, json_data):
        try:
            self.logger.info(f"******** _get_place_id 開始 ********")

            if not json_data:
                raise ValueError("json_data がNoneです")

            # jsonファイルの中にある'results'の中からデータを抜く
            places = json_data.get('results', [])

            self.logger.debug(f"places:\n{places[:100]}")

            place_id_list = []

            for place in places:
                self.logger.debug(f"place:\n{place}")

                # columnごとの値
                plase_id_value = place.get('place_id')
                self.logger.warning(f"column_value: {plase_id_value}")

                place_id_list.append(plase_id_value)

            self.logger.warning(f"place_id_list: {place_id_list}")


            self.logger.info(f"******** _get_place_id 終了 ********")

            return place_id_list


        except KeyError as ke:
            self.logger.error(f"指定されたカラムにエラーがあります: {ke}")

        except ValueError as ve:
            self.logger.error(f"指定したcolumnのデータが指定したJSONファイルにない: {ve}")

        except Exception as e:
            self.logger.error(f"_get_place_id 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# place_idのリストそれぞれでリクエストを行い詳細データをリスト化する

    def _place_id_requests_in_list(self, place_id_list):
        try:
            self.logger.info(f"******** get_results_in_place_id_list 開始 ********")

            self.logger.debug(f"place_id_list: {place_id_list[:20]}")

            place_details_results_list = []

            # 詳細データをリスト化する
            for place_id in place_id_list:
                # place_idでリクエスト
                place_details = self._place_id_request(place_id=place_id)
                self.logger.warning(f"place_details: \n{place_details}")
                place_details_results_list.append(place_details)

            self.logger.debug(f"place_details_results_list: \n{place_details_results_list[:100]}")

            self.logger.info(f"******** get_results_in_place_id_list 終了 ********")

            return place_details_results_list


        except Exception as e:
            self.logger.error(f"get_results_in_place_id_list 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------

# plase_idを使ってrequestをして詳細情報を取得

    def _place_id_request(self, place_id):
        try:
            self.logger.info(f"******** _plase_id_request 開始 ********")
            endpoint_url = const.place_details_endpoint_url

            params = {
                'place_id' : place_id,  # IDによる詳細情報を取得
                'key' : self.api_key
            }

            response = requests.get(endpoint_url, params=params, timeout=10)

            # ステータスコードが成功ならjsonを返す
            if response.status_code == 200:
                json_data = response.json()

                self.logger.info(f"******** _plase_id_request 終了 ********")

                return json_data


            elif response.status_code == 500:
                self.logger.error(f"_plase_id_request サーバーエラー")

            else:
                self.logger.error(f"_plase_id_request リクエストした際にエラーが発生: {response.status_code} - {response.text}")


            self.logger.info(f"******** _plase_id_request 終了 ********")

        except requests.exceptions.Timeout:
            self.logger.error(f"_plase_id_request リクエストでのタイムアウトエラー")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"_plase_id_request リクエストエラーが発生: {e}")

        except Exception as e:
            self.logger.error(f"_plase_id_request 処理中にエラーが発生: {e}")

        finally:
            self.logger.info(f"******** _plase_id_request 終了 ********")

        return None


# ----------------------------------------------------------------------------------
# place_details_dataからresults部分を抽出してリスト化する

    def _get_results_list(self, place_details_results_list):
        try:
            self.logger.info(f"******** _get_results_list 開始 ********")

            self.logger.debug(f"place_details_results_list: {place_details_results_list[:20]}")

            results_data_list = []

            # results部分を抽出してリストに追加
            for place_details in place_details_results_list:
                if 'result' in place_details:
                    self.logger.warning(place_details['result'])
                    results_data_list.append(place_details['result'])

            self.logger.debug(f"results_data: {results_data_list[:20]}")

            self.logger.info(f"******** _get_results_list 終了 ********")

            return results_data_list


        except Exception as e:
            self.logger.error(f"_get_results_list 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# DataFrameにする

    def _to_df(self, list_data, new_column):
        try:
            self.logger.info(f"******** _to_df 開始 ********")

            self.logger.debug(f"list_data: {list_data}")

            series_df = pd.DataFrame(list_data, columns=[new_column])

            self.logger.debug(series_df.head())

            self.logger.info(f"******** _to_df 終了 ********")

            return series_df

        except Exception as e:
            self.logger.error(f"_to_df 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# 既存のDataFrameに結合させる

    def _df_marge(self, key_df, add_df):
        try:
            self.logger.info(f"******** _df_marge 開始 ********")

            self.logger.debug(f"key_df: \n{key_df.head(3)}")
            self.logger.debug(f"add_df: \n{add_df.head(3)}")

            new_df = pd.merge(key_df, add_df, left_index=True, right_index=True, how='left')

            self.logger.warning(f"new_df: \n{new_df.head(3)}")

            self.logger.info(f"******** _df_marge 終了 ********")

            return new_df

        except Exception as e:
            self.logger.error(f"_df_marge 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# DataFrameからcolumnデータを抽出

    def _get_column_data(self, key_df, column):
        try:
            self.logger.info(f"******** _get_column_data 開始 ********")

            self.logger.debug(f"key_df: \n{key_df.head(3)}")

            series_data = key_df[column]

            self.logger.debug(f"series_data: \n{series_data[3]}")

            self.logger.info(f"******** _get_column_data 終了 ********")

            return series_data

        except Exception as e:
            self.logger.error(f"_get_column_data 処理中にエラーが発生: {e}")



# ----------------------------------------------------------------------------------
# 住所を日本語に変換するためにGeocoding APIを通す

    def _address_to_japanese(self, address):
        try:
            self.logger.info(f"******** address_to_japanese 開始 ********")

            self.logger.debug(f"list_data: {address}")

            endpoint_url = const.geocoding_endpoint_url

            self.logger.warning(f"endpoint_url: {endpoint_url}")

            params ={
                'address' : address,
                'key' : self.api_key,
                'language' : 'ja'
            }

            # Geocodingへリクエスト
            response = requests.get(endpoint_url, params=params)

            # 送信のステータスcodeがOKだったら
            if response.status_code == 200:
                response_json = response.json()
                self.logger.info("リクエスト成功")

                self.logger.info(response_json)

                # ステータスがOKだったら
                if response_json['status'] == 'OK':
                    self.logger.info("ステータスOK")

                    # jsonデータのresultsの中のformatted_addressを取得
                    formatted_address = response_json['results'][0]['formatted_address']
                    self.logger.warning(f"formatted_address: {formatted_address}")

                    # 余計な文字を除去
                    clean_address = self._str_Remove(value=formatted_address, str_remove="日本、")

                    self.logger.info(f"******** address_to_japanese 終了 ********")

                    return clean_address

                else:
                    raise Exception(f"ステータスがOKになってない {response_json['status']}")

            else:
                raise Exception(f"リクエスト中にエラーが発生 {response.status_code}")


        except Exception as e:
            self.logger.error(f"address_to_japanese 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
# 余計な文字が入るためクリーニング

    def _str_Remove(self, value, str_remove):
        try:
            self.logger.info(f"******** _str_Remove 開始 ********")

            self.logger.debug(f"str_remove: {str_remove}")

            if str_remove in value:
                self.logger.info(f"{value} に {str_remove} を発見")

                # 対象の文字を除去
                remove_value = value.replace(str_remove, "")
                self.logger.debug(f"remove_value: {remove_value}")
                return remove_value

            else:
                self.logger.error(f"{value} には {str_remove} はありません。")

            self.logger.info(f"******** _str_Remove 終了 ********")

            return value

        except Exception as e:
            self.logger.error(f"_str_Remove 処理中にエラーが発生: {e}")
            raise


# ----------------------------------------------------------------------------------
# 各リストに処理を当て込めていく

    def add_process_value_in_list(self, list_data, add_func):
        try:
            self.logger.info(f"******** DfProcessMerge 開始 ********")

            self.logger.debug(f"list_data: {list_data}")

            original_data_list = []

            # 値に処理を加えてリストにまとめる
            for data in list_data:
                original_data = add_func(data)
                self.logger.info(f"original_data: {original_data}")
                original_data_list.append(original_data)

            self.logger.info(f"original_data_list: {original_data_list}")

            self.logger.info(f"******** DfProcessMerge 終了 ********")

            return original_data_list

        except Exception as e:
            self.logger.error(f"DfProcessMerge 処理中にエラーが発生: {e}")

# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------



# ----------------------------------------------------------------------------------
# Google mapAPIでjson取得
# jsonからplase_idを取得
# plase_idから詳細が掲載されてるjsonを取得
# jsonからDataFrameへ変換
# DataFrameから行ごとのデータをリストへ変換する

    def get_gm_df_list(self, query, columns):
        try:
            self.logger.info(f"******** get_gm_df_list 開始 ********")


            # gmAPIリクエスト
            json_data = self._google_map_api_request(query=query)
            time.sleep(2)

            # plase_id_listを取得
            plase_id_list = self._get_place_id(json_data=json_data)
            time.sleep(2)

            # 詳細データを取得
            details_data_list = self._place_id_requests_in_list(place_id_list=plase_id_list)
            time.sleep(2)

            # 詳細データリストからresult部分を抽出してリストを作成
            results_data_list= self._get_results_list(place_details_results_list=details_data_list)
            time.sleep(2)


            # 詳細データをDataFrameに変換
            df = self._get_json_to_dataframe(json_data=results_data_list)
            time.sleep(2)

            #! 変換しなければならない箇所
            # 住所→formatted_addressをGoogle Maps Geocoding APIを使うことで日本語変換する→dfにして結合

            #TODO 営業時間
            #TODO 定休日

            #TODO レビュ→profile_photo_url, author_name, rating, text, →それぞれの項目を作成なし（-）

            #TODO 写真→ありなし
            #TODO website→ありなし



            # DataFrameから必要なcolumn情報をリストにして取得
            self.get_column_data_in_df(df=df, columns=columns)
            time.sleep(2)


            self.logger.info(f"******** get_gm_df_list 終了 ********")

        except Exception as e:
            self.logger.error(f"get_gm_df_list 処理中にエラーが発生: {e}")


# ----------------------------------------------------------------------------------
