from __future__ import annotations
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from .forms import CalcForm
from .models import Calculation
from .utils import estimate_hand_value

def _melds_to_json(melds_text: str):
    lines = [ln.strip() for ln in (melds_text or "").splitlines() if ln.strip()]
    melds = []
    for ln in lines:
        parts = ln.split()
        if len(parts) == 3:
            melds.append({"type": parts[0], "tiles": parts[1], "open": parts[2]})
        else:
            melds.append({"raw": ln})
    return melds

def _first_form_error(form: CalcForm) -> str:
    for errs in form.errors.values():
        if errs:
            return str(errs[0])
    return "入力が不正です。"

@login_required
def home(request):
    last_items = Calculation.objects.filter(user=request.user).only("id","created_at","hand_text","win_tile_text")[:10]

    if request.method == "POST":
        is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
        form = CalcForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                res = estimate_hand_value(
                    hand_text=cd["hand_text"],
                    win_tile_text=cd["win_tile_text"],
                    melds_text=cd.get("melds_text") or "",
                    is_tsumo=(cd["win_type"] == "tsumo"),
                    is_dealer=bool(cd.get("is_dealer")),
                    round_wind=cd["round_wind"],
                    self_wind=cd["self_wind"],
                    dora_text=cd.get("dora_text") or "",
                    ura_dora_text=cd.get("ura_dora_text") or "",
                    aka_dora_count=cd.get("aka_dora_count") or 0,
                    is_riichi=bool(cd.get("is_riichi")),
                    honba=cd.get("honba") or 0,
                    riichi_sticks=cd.get("riichi_sticks") or 0,
                    allow_open_tanyao=(cd.get("open_tanyao_rule") == "on"),
                )
            except Exception as e:
                if is_ajax:
                    return JsonResponse({"ok": False, "error": str(e)}, status=400)
                messages.error(request, str(e))
                return render(request, "calcapp/home.html", {"form": form, "last_items": last_items})

            with transaction.atomic():
                obj = Calculation.objects.create(
                    user=request.user,
                    hand_text=cd["hand_text"],
                    win_tile_text=cd["win_tile_text"],
                    melds_json=_melds_to_json(cd.get("melds_text") or ""),
                    config_json={
                        "win_type": cd["win_type"],
                        "is_dealer": bool(cd.get("is_dealer")),
                        "round_wind": cd["round_wind"],
                        "self_wind": cd["self_wind"],
                        "dora_text": cd.get("dora_text") or "",
                        "ura_dora_text": cd.get("ura_dora_text") or "",
                        "aka_dora_count": cd.get("aka_dora_count") or 0,
                        "is_riichi": bool(cd.get("is_riichi")),
                        "honba": cd.get("honba") or 0,
                        "riichi_sticks": cd.get("riichi_sticks") or 0,
                        "open_tanyao_rule": cd.get("open_tanyao_rule"),
                    },
                    result_json=res,
                )
            if is_ajax:
                return JsonResponse({"ok": True, "id": obj.pk, "result": res})
            messages.success(request, "計算結果を保存しました。")
            return redirect("calcapp:history_detail", pk=obj.pk)
        if is_ajax:
            return JsonResponse({"ok": False, "error": _first_form_error(form)}, status=400)
    else:
        form = CalcForm()

    return render(request, "calcapp/home.html", {"form": form, "last_items": last_items})

@login_required
def history_list(request):
    items = Calculation.objects.filter(user=request.user).only("id","created_at","hand_text","win_tile_text")
    return render(request, "calcapp/history_list.html", {"items": items})

@login_required
def history_detail(request, pk: int):
    obj = get_object_or_404(Calculation, pk=pk, user=request.user)
    return render(request, "calcapp/history_detail.html", {"obj": obj})

@login_required
def history_delete(request, pk: int):
    obj = get_object_or_404(Calculation, pk=pk, user=request.user)
    if request.method == "POST":
        obj.delete()
        messages.success(request, "削除しました。")
        return redirect("calcapp:history_list")
    return render(request, "calcapp/history_confirm_delete.html", {"obj": obj})
