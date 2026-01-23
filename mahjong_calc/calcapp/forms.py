from django import forms
from django.core.exceptions import ValidationError

WIND_CHOICES = [("E","東"),("S","南"),("W","西"),("N","北")]
TSUMO_CHOICES = [("ron","ロン"),("tsumo","ツモ")]
OPEN_TANYAO_CHOICES = [("on","あり（喰い断OK）"),("off","なし（喰い断NG）")]

class CalcForm(forms.Form):
    hand_text = forms.CharField(label="手牌（14枚）", max_length=200)
    win_tile_text = forms.CharField(label="和了牌", max_length=10)
    melds_text = forms.CharField(label="鳴き（1行1面子）", required=False, widget=forms.Textarea(attrs={"rows":4}))

    win_type = forms.ChoiceField(label="和了方法", choices=TSUMO_CHOICES, initial="ron")
    is_dealer = forms.BooleanField(label="親（東）", required=False)
    round_wind = forms.ChoiceField(label="場風", choices=WIND_CHOICES, initial="E")
    self_wind = forms.ChoiceField(label="自風", choices=WIND_CHOICES, initial="S")

    dora_text = forms.CharField(label="ドラ表示牌（CSV）", required=False)
    ura_dora_text = forms.CharField(label="裏ドラ表示牌（CSV）", required=False)
    aka_dora_count = forms.IntegerField(label="赤ドラ枚数", required=False, min_value=0, max_value=3, initial=0)
    is_riichi = forms.BooleanField(label="リーチ", required=False)
    honba = forms.IntegerField(label="本場", min_value=0, max_value=20, initial=0)
    riichi_sticks = forms.IntegerField(label="供託（リーチ棒）", min_value=0, max_value=20, initial=0)
    open_tanyao_rule = forms.ChoiceField(label="喰い断ルール", choices=OPEN_TANYAO_CHOICES, initial="on")

    def clean(self):
        cd = super().clean()
        is_dealer = cd.get("is_dealer") or False
        sw = cd.get("self_wind")
        if is_dealer and sw != "E":
            raise ValidationError("親の場合、自風は東(E)にしてください。")
        if (not is_dealer) and sw == "E":
            raise ValidationError("自風が東(E)なら親です。親にチェックしてください。")
        return cd
