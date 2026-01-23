from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .utils import calculate_hand_score
from .models import CalculationHistory
from mahjong.constants import EAST, SOUTH, WEST, NORTH

@login_required
def index(request):
    context = {}
    if request.method == 'POST':
        # Extract data from POST
        hand_str = request.POST.get('hand_str')
        win_tile = request.POST.get('win_tile')
        melds_str = request.POST.get('melds_str', '')
        is_tsumo = request.POST.get('is_tsumo') == 'on'
        is_riichi = request.POST.get('is_riichi') == 'on'
        
        # Wind mapping
        wind_map = {'east': EAST, 'south': SOUTH, 'west': WEST, 'north': NORTH}
        player_wind = wind_map.get(request.POST.get('player_wind'), EAST)
        round_wind = wind_map.get(request.POST.get('round_wind'), EAST)
        
        # Calculate
        if hand_str and win_tile:
            result = calculate_hand_score(
                hand_str=hand_str,
                win_tile=win_tile,
                melds_str=melds_str,
                is_tsumo=is_tsumo,
                is_riichi=is_riichi,
                player_wind=player_wind,
                round_wind=round_wind
            )
            
            context['result'] = result
            context['hand_str'] = hand_str
            context['win_tile'] = win_tile
            
            # Save History
            if not result.get('error'):
                CalculationHistory.objects.create(
                    user=request.user,
                    hand_image={'hand': hand_str, 'win_tile': win_tile},
                    result_data=result
                )

    return render(request, 'calculator/index.html', context)

@login_required
def history_list(request):
    history = CalculationHistory.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'calculator/history_list.html', {'history': history})
