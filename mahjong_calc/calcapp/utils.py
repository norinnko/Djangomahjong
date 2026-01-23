from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Any
import re

from mahjong.hand_calculating.hand import HandCalculator
from mahjong.tile import TilesConverter
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH

_TILE_RE = re.compile(r"^[0-9]+[mpsz](?:[0-9]+[mpsz])*$")

def _normalize(s: str) -> str:
    return (s or "").strip().replace(" ", "").replace("\t", "").lower()

def parse_compact_tiles(tile_str: str) -> List[str]:
    """
    Compact: '123m456p789s11z55m' -> ['1m','2m','3m',...]
    '0' is allowed for red five.
    """
    s = _normalize(tile_str)
    if not s:
        raise ValueError("牌文字列が空です。")
    if not _TILE_RE.match(s):
        raise ValueError("牌表記が不正です。例: 123m456p789s11z55m")
    buf = ""
    out: List[str] = []
    for ch in s:
        if ch.isdigit():
            buf += ch
            continue
        if ch not in "mpsz":
            raise ValueError("牌表記が不正です。")
        if not buf:
            raise ValueError("牌表記が不正です（数字の後にm/p/s/z）。")
        for d in buf:
            out.append(f"{d}{ch}")
        buf = ""
    if buf:
        raise ValueError("牌表記が不正です（末尾に数字が残っています）。")
    return out

def tile_code_to_34(tile: str) -> int:
    if len(tile) != 2:
        raise ValueError(f"牌が不正です: {tile}")
    d, suit = tile[0], tile[1]
    if d == "0":
        d = "5"
    n = int(d)
    if suit in "mps":
        if not (1 <= n <= 9):
            raise ValueError(f"数牌が不正です: {tile}")
    elif suit == "z":
        if not (1 <= n <= 7):
            raise ValueError(f"字牌が不正です: {tile}")
    else:
        raise ValueError(f"牌が不正です: {tile}")

    if suit == "m":
        return n - 1
    if suit == "p":
        return 9 + (n - 1)
    if suit == "s":
        return 18 + (n - 1)
    return 27 + (n - 1)

def split_tiles_by_suit(tiles: List[str]) -> Dict[str, List[str]]:
    suits = {"m": [], "p": [], "s": [], "z": []}
    for t in tiles:
        suits[t[1]].append(t[0])
    return suits

def _count_tiles_34(tiles: List[str]) -> List[int]:
    c = [0] * 34
    for t in tiles:
        c[tile_code_to_34(t)] += 1
    return c

def _validate_max4(tiles: List[str]) -> None:
    c = _count_tiles_34(tiles)
    if any(v > 4 for v in c):
        raise ValueError("同じ牌は最大4枚までです。入力が不正です。")

@dataclass
class ParsedMeld:
    meld_type: str   # chi/pon/kan
    tiles: List[str]
    opened: bool

def parse_melds_text(melds_text: str) -> List[ParsedMeld]:
    """
    Lines:
      chi 123m open
      pon 777p open
      kan 9999s closed
    """
    s = (melds_text or "").strip()
    if not s:
        return []
    melds: List[ParsedMeld] = []
    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 3:
            raise ValueError(f"鳴きの形式が不正です: '{line}'（例: pon 777m open）")
        mtype, tiles_str, oc = parts[0].lower(), parts[1].lower(), parts[2].lower()
        if mtype not in ("chi", "pon", "kan"):
            raise ValueError(f"鳴き種別が不正です: '{mtype}'（chi/pon/kan）")
        if oc not in ("open", "closed"):
            raise ValueError(f"open/closed が不正です: '{oc}'")
        opened = oc == "open"
        tiles_codes = parse_compact_tiles(tiles_str)

        if mtype == "chi":
            if len(tiles_codes) != 3:
                raise ValueError(f"チーは3枚です: '{line}'")
            if any(t[1] == "z" for t in tiles_codes):
                raise ValueError(f"チーは字牌でできません: '{line}'")
            suit = tiles_codes[0][1]
            if any(t[1] != suit for t in tiles_codes):
                raise ValueError(f"チーは同一の色で: '{line}'")
            nums = sorted(int(("5" if t[0] == "0" else t[0])) for t in tiles_codes)
            if nums[0] + 1 != nums[1] or nums[1] + 1 != nums[2]:
                raise ValueError(f"チーは連続する3枚です: '{line}'")
            if not opened:
                raise ValueError(f"チーは open のみです: '{line}'")
        elif mtype == "pon":
            if len(tiles_codes) != 3:
                raise ValueError(f"ポンは3枚です: '{line}'")
            a = tile_code_to_34(tiles_codes[0])
            if any(tile_code_to_34(t) != a for t in tiles_codes):
                raise ValueError(f"ポンは同じ牌3枚です: '{line}'")
            if not opened:
                raise ValueError(f"ポンは open のみです: '{line}'")
        else:
            if len(tiles_codes) != 4:
                raise ValueError(f"カンは4枚です: '{line}'")
            a = tile_code_to_34(tiles_codes[0])
            if any(tile_code_to_34(t) != a for t in tiles_codes):
                raise ValueError(f"カンは同じ牌4枚です: '{line}'")

        melds.append(ParsedMeld(meld_type=mtype, tiles=tiles_codes, opened=opened))
    return melds

def subtract_tiles(source: List[str], to_remove: List[str]) -> List[str]:
    remove_counts = [0] * 34
    for t in to_remove:
        remove_counts[tile_code_to_34(t)] += 1

    kept: List[str] = []
    for t in source:
        idx = tile_code_to_34(t)
        if remove_counts[idx] > 0:
            remove_counts[idx] -= 1
        else:
            kept.append(t)

    if any(v > 0 for v in remove_counts):
        raise ValueError("鳴き牌が手牌に含まれていません（差し引きできません）。手牌は14枚（鳴き含む）で入力してください。")
    return kept

_WIND_MAP = {"E": EAST, "S": SOUTH, "W": WEST, "N": NORTH}

def _to_converter_strings(tiles: List[str], aka_dora_count: int) -> Dict[str, str]:
    suits = split_tiles_by_suit(tiles)

    # Convert some '5' to '0' for aka dora (m/p/s only)
    need = int(aka_dora_count or 0)
    for suit in ("m", "p", "s"):
        if need <= 0:
            break
        digits = suits[suit]
        for i in range(len(digits)):
            if need <= 0:
                break
            if digits[i] == "5":
                digits[i] = "0"
                need -= 1
        suits[suit] = digits

    if need > 0:
        raise ValueError("赤ドラ枚数が多すぎます。手牌（萬/筒/索）の5が不足しています。")

    return {
        "man": "".join(suits["m"]),
        "pin": "".join(suits["p"]),
        "sou": "".join(suits["s"]),
        "honors": "".join(suits["z"]),
    }

def _tile_code_to_136_one(tile: str) -> int:
    t = tile.strip().lower()
    if len(t) != 2:
        raise ValueError(f"牌が不正です: {tile}")
    d, suit = t[0], t[1]
    if suit == "m":
        arr = TilesConverter.string_to_136_array(man=d)
    elif suit == "p":
        arr = TilesConverter.string_to_136_array(pin=d)
    elif suit == "s":
        arr = TilesConverter.string_to_136_array(sou=d)
    elif suit == "z":
        arr = TilesConverter.string_to_136_array(honors=d)
    else:
        raise ValueError(f"牌が不正です: {tile}")
    if not arr:
        raise ValueError(f"牌が不正です: {tile}")
    return arr[0]

def parse_tile_list_csv(s: str) -> List[str]:
    s = (s or "").strip()
    if not s:
        return []
    parts = [p.strip().lower() for p in s.split(",") if p.strip()]
    for p in parts:
        if len(p) != 2 or p[1] not in "mpsz" or not p[0].isdigit():
            raise ValueError(f"ドラ表示牌が不正です: {p}")
    return parts

def build_explanation(yaku_names: List[str], is_riichi: bool, melds: List[ParsedMeld], dora_indicators: List[str], ura_dora: List[str], fu_details: List[dict]) -> str:
    lines: List[str] = []
    if yaku_names:
        lines.append("この手の役は「" + "、".join(yaku_names) + "」です。")
    else:
        lines.append("役が見つからない（または入力が不正）可能性があります。")
    if melds:
        if any(m.opened for m in melds):
            lines.append("鳴き（明副露）があるため、門前限定の役（例：立直など）は成立しません。")
        else:
            lines.append("暗槓のみなので門前扱いになります。")
    if is_riichi:
        lines.append("リーチ指定のため、裏ドラも加算されます（入力がある場合）。")
    if dora_indicators:
        lines.append("ドラ表示牌: " + ", ".join(dora_indicators))
    if is_riichi and ura_dora:
        lines.append("裏ドラ表示牌: " + ", ".join(ura_dora))
    if fu_details:
        lines.append("符の内訳（簡易）: " + " + ".join([f"{x.get('fu')}符({x.get('reason')})" for x in fu_details]))
    return "\n".join(lines)

def estimate_hand_value(
    hand_text: str,
    win_tile_text: str,
    melds_text: str,
    is_tsumo: bool,
    is_dealer: bool,
    round_wind: str,
    self_wind: str,
    dora_text: str,
    ura_dora_text: str,
    aka_dora_count: int,
    is_riichi: bool,
    honba: int,
    riichi_sticks: int,
    allow_open_tanyao: bool,
) -> Dict[str, Any]:
    tiles_all = parse_compact_tiles(hand_text)
    if len(tiles_all) != 14:
        raise ValueError("手牌は14枚で入力してください（鳴き牌も含めてOK）。")
    _validate_max4(tiles_all)

    win_tile_text = _normalize(win_tile_text)
    if len(win_tile_text) != 2 or win_tile_text[1] not in "mpsz" or not win_tile_text[0].isdigit():
        raise ValueError("和了牌が不正です。例: 5m")
    win34 = tile_code_to_34(win_tile_text)

    parsed_melds = parse_melds_text(melds_text)
    meld_tiles_flat: List[str] = []
    for m in parsed_melds:
        meld_tiles_flat.extend(m.tiles)

    tiles_concealed = subtract_tiles(tiles_all, meld_tiles_flat)
    expected_concealed = 14 - len(meld_tiles_flat)
    if len(tiles_concealed) != expected_concealed:
        raise ValueError("手牌と鳴きの枚数が合いません。手牌は14枚（鳴き含む）で入力してください。")

    if _count_tiles_34(tiles_concealed)[win34] <= 0:
        raise ValueError("和了牌が手牌に含まれていません（鳴き分を除いた残りに必要）。")

    open_hand = any(m.opened for m in parsed_melds)
    if open_hand and is_riichi:
        raise ValueError("鳴き（open）がある手はリーチできません（MVP簡易ルール）。")

    conv = _to_converter_strings(tiles_concealed, aka_dora_count)
    tiles_136 = TilesConverter.string_to_136_array(
        man=conv["man"], pin=conv["pin"], sou=conv["sou"], honors=conv["honors"]
    )

    win_tile_id = None
    for t in tiles_136:
        if t // 4 == win34:
            win_tile_id = t
            break
    if win_tile_id is None:
        raise ValueError("内部変換エラー: 和了牌が見つかりません。")

    # Melds
    melds_lib: List[Meld] = []
    for m in parsed_melds:
        mconv = _to_converter_strings(m.tiles, aka_dora_count=0)
        meld_136 = TilesConverter.string_to_136_array(
            man=mconv["man"], pin=mconv["pin"], sou=mconv["sou"], honors=mconv["honors"]
        )
        if m.meld_type == "chi":
            melds_lib.append(Meld(meld_type=Meld.CHI, tiles=meld_136, opened=True))
        elif m.meld_type == "pon":
            melds_lib.append(Meld(meld_type=Meld.PON, tiles=meld_136, opened=True))
        else:
            melds_lib.append(Meld(meld_type=Meld.KAN, tiles=meld_136, opened=m.opened))

    dora_ind = parse_tile_list_csv(dora_text)
    ura_dora_ind = parse_tile_list_csv(ura_dora_text)

    dora_136: List[int] = []
    for t in dora_ind:
        dora_136.append(_tile_code_to_136_one(t))
    if is_riichi:
        for t in ura_dora_ind:
            dora_136.append(_tile_code_to_136_one(t))

    options = OptionalRules(
        has_open_tanyao=bool(allow_open_tanyao),
        has_aka_dora=True,
    )
    config = HandConfig(
        is_tsumo=bool(is_tsumo),
        is_riichi=bool(is_riichi),
        player_wind=_WIND_MAP[self_wind],
        round_wind=_WIND_MAP[round_wind],
        options=options,
    )

    calculator = HandCalculator()
    result = calculator.estimate_hand_value(
        tiles_136,
        win_tile_id,
        melds=melds_lib or None,
        dora_indicators=dora_136 or None,
        config=config,
    )

    err = getattr(result, "error", None)
    if err:
        raise ValueError(f"計算できませんでした: {err}")

    han = int(getattr(result, "han", 0) or 0)
    fu = int(getattr(result, "fu", 0) or 0)
    cost = getattr(result, "cost", {}) or {}
    yaku = getattr(result, "yaku", []) or []
    fu_details = getattr(result, "fu_details", []) or []

    base_cost = {"main": int(cost.get("main") or 0), "additional": int(cost.get("additional") or 0)}
    honba = int(honba or 0)
    sticks = int(riichi_sticks or 0)

    payout: Dict[str, Any] = {"type": "ron" if not is_tsumo else "tsumo"}
    if not is_tsumo:
        pay_from_loser = base_cost["main"] + honba * 300
        payout["pay_from_loser"] = pay_from_loser
        payout["riichi_sticks_bonus"] = sticks * 1000
        payout["total_gain"] = pay_from_loser + sticks * 1000
    else:
        if is_dealer:
            each = base_cost["main"] + honba * 100
            payout["each_pay"] = each
            payout["riichi_sticks_bonus"] = sticks * 1000
            payout["total_gain"] = each * 3 + sticks * 1000
        else:
            dealer_pay = base_cost["main"] + honba * 100
            other_pay = base_cost["additional"] + honba * 100
            payout["dealer_pay"] = dealer_pay
            payout["non_dealer_pay"] = other_pay
            payout["riichi_sticks_bonus"] = sticks * 1000
            payout["total_gain"] = dealer_pay + other_pay * 2 + sticks * 1000

    yaku_names = [str(y) for y in yaku]
    explain_text = build_explanation(
        yaku_names=yaku_names,
        is_riichi=is_riichi,
        melds=parsed_melds,
        dora_indicators=dora_ind,
        ura_dora=ura_dora_ind,
        fu_details=fu_details,
    )

    return {
        "han": han,
        "fu": fu,
        "yaku_names": yaku_names,
        "fu_details": fu_details,
        "base_cost": base_cost,
        "payout": payout,
        "explain_text": explain_text,
        "open_hand": open_hand,
        "dora_used": dora_ind,
        "ura_dora_used": ura_dora_ind if is_riichi else [],
    }
