import streamlit as st
import asyncio
from Generator import ArtifacterGenerator
from enkanetwork.exception import *
import logging
import asyncio

logger = logging.getLogger()



async def main():
  gen_client = ArtifacterGenerator(cwd=".")
  if "player_info" not in st.session_state:
    st.session_state.player_info = False
  params = st.experimental_get_query_params()
  if params.get("uid"):
    queryUID = params["uid"][0]
  else:
    queryUID = None

  st.set_page_config(
    page_title="Artifacter on Web",
    page_icon="Assets/kuroneko-logo.webp",
    layout="wide",
    initial_sidebar_state="collapsed"
  )
  st.markdown(
    """
<style>
    [data-testid="collapsedControl"] {
        display: none
    }
</style>
""",
    unsafe_allow_html=True,
    )
  try:
    await on_start()
  except:
    pass
  content = """
  # Web版 Artifacter
  [![Twitter](https://img.shields.io/badge/Artifacter-%40ArtifacterBot-1DA1F2?logo=twitter&style=flat-square)](https://twitter.com/ArtifacterBot)
  [![Twitter](https://img.shields.io/badge/開発-%40__0kq__-1DA1F2?logo=twitter&style=flat-square)](https://twitter.com/_0kq_)
  [![Twitter](https://img.shields.io/badge/運営・変更-%40kuroneko_server-1DA1F2?logo=twitter&style=flat-square)](https://twitter.com/kuroneko_server)
  [![Discord](https://img.shields.io/discord/867038364552396860?logo=Discord&label=Discord&style=flat-square)](https://discord.com/invite/Y6w5Jv3EAR)
  [![Donation](https://img.shields.io/badge/%E9%81%8B%E5%96%B6%E6%94%AF%E6%8F%B4-Donation-green?style=flat-square)](https://kuroneko6423.com/donation)
  [![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fartifacter-builder.kuroneko6423.com&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=%E3%82%A2%E3%82%AF%E3%82%BB%E3%82%B9%E6%95%B0&edge_flat=false)](https://hits.seeyoufarm.com)
  ##### 原神のUIDからビルドカードを生成できます  
  ※バグ報告は[Discord](https://discord.com/invite/Y6w5Jv3EAR)からお願いします
  """
  st.write(content,unsafe_allow_html=True)
  UID = st.text_input("UIDを入力",value=queryUID if queryUID else "")
  queryUID = None
  if UID:
    st.experimental_set_query_params(uid=UID)
  if st.button("プレイヤー情報の取得", key="get_player_info",on_click=session_player) or st.session_state.player_info:
      placeholder = st.empty()
      placeholder.write("プレイヤー情報を取得中...")
      try:
        async with gen_client.client:
          player_data = await gen_client.client.fetch_user_by_uid(UID)
      except EnkaServerRateLimit:
        placeholder.empty()
        st.write("レートリミットに達しました。")
        return
      except EnkaServerMaintanance:
        placeholder.empty()
        st.write("EnkaNetworkがメンテナンス中です。")
        return
      except EnkaPlayerNotFound:
        placeholder.empty()
        st.write("プレイヤーが見つかりませんでした。")
        return
      except EnkaServerError:
        placeholder.empty()
        st.write("EnkaNetworkでエラーが発生しました。")
        return
      except Exception as e:
        placeholder.empty()
        st.write(f"プレイヤー情報の取得に失敗しました。{e}")
        return
      placeholder.empty()
      player_info = f"""
### プレイヤー情報
##### {player_data.player.nickname} Lv.{player_data.player.level}
- 世界ランク{player_data.player.world_level}
- 螺旋 {player_data.player.abyss_floor}-{player_data.player.abyss_room}
- アチーブメント数 {player_data.player.achievement}
"""
      st.write(player_info)
      if player_data.characters:
        characters = {v.name+" Lv."+str(v.level): v for v in player_data.characters}
        character = st.selectbox("キャラクターを選択", characters.keys())
        character_info = f"""
### キャラクター情報
##### {characters[character].name} Lv.{characters[character].level}
- HP: {round(characters[character].stats.FIGHT_PROP_MAX_HP.value)}
- 命ノ星座: {characters[character].constellations_unlocked}凸
- HP: {round(characters[character].stats.FIGHT_PROP_MAX_HP.value)}
- 攻撃力: {round(characters[character].stats.FIGHT_PROP_CUR_ATTACK.value)}
- 防御力: {round(characters[character].stats.FIGHT_PROP_CUR_DEFENSE.value)}
- 元素熟知: {round(characters[character].stats.FIGHT_PROP_ELEMENT_MASTERY.value)}
- 会心率: {round(characters[character].stats.FIGHT_PROP_CRITICAL.value*100,1)}%
- 会心ダメージ: {round(characters[character].stats.FIGHT_PROP_CRITICAL_HURT.value*100,1)}%
- 元素チャージ効率: {round(characters[character].stats.FIGHT_PROP_CHARGE_EFFICIENCY.value*100,1)}%
##### {characters[character].equipments[-1].detail.name} Lv.{characters[character].equipments[-1].level}
- 精錬ランク: {characters[character].equipments[-1].refinement}
- 基礎攻撃力: {round(characters[character].equipments[-1].detail.mainstats.value)}
"""
        if characters[character].equipments[-1].detail.substats:
          character_info += f"- {characters[character].equipments[-1].detail.substats[0].name}: {characters[character].equipments[-1].detail.substats[0].value}"
        st.write(character_info)
        score_types = {"攻撃力": "ATTACK", "防御力": "DEFENSE", "HP": "HP", "元素チャージ効率": "EFFICIENCY", "元素熟知": "ELEMENT"}
        score_type = st.selectbox("スコア計算", score_types.keys())
        if st.button("ビルドカードを生成"):
          placeholder = st.empty()
          placeholder.write("ビルドカードを生成中...")
          Image = gen_client.generation(characters[character],score_types[score_type],None)
          placeholder.image(Image)
          st.write("画像を長押し / 右クリックで保存できます。")
      else:
        st.write("キャラクター情報の取得に失敗しました。")

def session_player():
  st.session_state.player_info = True

def gen_image(client,character):
  st.write("ビルドカードを生成中...")
  Image = client.generation(character,score_type="ATTACK")
  st.image(Image)


if __name__ == "__main__":
  loop = asyncio.new_event_loop()
  loop.run_until_complete(main())
