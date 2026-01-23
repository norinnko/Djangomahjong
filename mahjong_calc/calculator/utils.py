from mahjong.hand_calculating.hand import HandCalculator
from mahjong.hand_calculating.hand_config import HandConfig, OptionalRules
from mahjong.tile import TilesConverter
from mahjong.meld import Meld
from mahjong.constants import EAST, SOUTH, WEST, NORTH

def parse_melds_string(melds_str):
    """
    Parse the melds string from frontend.
    
    Format: "type:tiles;type:tiles;..."
    e.g., "pon:555z;chi:123m"
    
    Returns list of Meld objects.
    """
    if not melds_str:
        return []
    
    melds = []
    meld_parts = melds_str.split(';')
    
    for part in meld_parts:
        if not part or ':' not in part:
            continue
        
        meld_type, tiles_str = part.split(':', 1)
        
        try:
            tiles_136 = TilesConverter.one_line_string_to_136_array(tiles_str)
        except Exception:
            continue
        
        if meld_type == 'chi':
            meld = Meld(meld_type=Meld.CHI, tiles=tiles_136, opened=True)
        elif meld_type == 'pon':
            meld = Meld(meld_type=Meld.PON, tiles=tiles_136, opened=True)
        elif meld_type == 'minkan':
            meld = Meld(meld_type=Meld.KAN, tiles=tiles_136, opened=True)
        elif meld_type == 'ankan':
            meld = Meld(meld_type=Meld.KAN, tiles=tiles_136, opened=False)
        else:
            continue
        
        melds.append(meld)
    
    return melds

def calculate_hand_score(hand_str, win_tile, melds_str='', is_tsumo=False, is_riichi=False, player_wind=EAST, round_wind=EAST, dora_indicators=None):
    """
    Parses input and calculates score using mahjong library.
    
    Args:
        hand_str (str): Manually constructed string of tiles (e.g., '123m456p789s11z'). 
                        This is a simplified input method for now.
        win_tile (str): The tile used to win (e.g., '1z').
        melds_str (str): String representation of melds (e.g., 'pon:555z;chi:123m').
        is_tsumo (bool): True if Tsumo, False if Ron.
        is_riichi (bool): True if Riichi.
        player_wind (int): 27=East, 28=South, 29=West, 30=North (mahjong lib constants).
        round_wind (int): Similar to player_wind.
        dora_indicators (list): List of dora indicator tiles.
    
    Returns:
        dict: Calculation result or error message.
    """
    
    calculator = HandCalculator()
    
    # Parse melds
    melds = parse_melds_string(melds_str)
    has_open_melds = any(m.opened for m in melds)
    
    # 1. Parse Hand Tiles
    try:
        tiles = TilesConverter.one_line_string_to_136_array(hand_str)
        win_tile_136 = TilesConverter.one_line_string_to_136_array(win_tile)[0]
    except Exception as e:
        return {'error': 'Invalid tile format'}

    # Add tiles from melds to get complete hand
    all_tiles = list(tiles)
    for meld in melds:
        all_tiles.extend(meld.tiles)

    # For the library, the `tiles` param should contain all tiles including melds
    # Then we specify melds separately
    
    # Combine hand tiles with win tile for complete evaluation
    full_hand = all_tiles + [win_tile_136]

    # 2. Config
    options = OptionalRules(
        has_open_tanyao=True,
        has_aka_dora=True, # Red fives
    )
    
    # Can't riichi with open hand
    actual_riichi = is_riichi and not has_open_melds
    
    config = HandConfig(
        is_tsumo=is_tsumo,
        is_riichi=actual_riichi,
        player_wind=player_wind,
        round_wind=round_wind,
        options=options
    )

    # 3. Calculate
    try:
        result = calculator.estimate_hand_value(
            tiles=full_hand,
            win_tile=win_tile_136,
            melds=melds if melds else None,
            dora_indicators=dora_indicators, 
            config=config
        )
    except Exception as e:
        return {'error': str(e)}

    if result.error:
        return {'error': result.error}

    return {
        'han': result.han,
        'fu': result.fu,
        'cost': result.cost,
        'yaku': [str(y) for y in result.yaku],
        'error': None
    }
