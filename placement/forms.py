import re
from datetime import date

from django import forms

from .models import Participant


def validate_phone(value):
    digits = re.sub(r"\D", "", value)

    # Поддерживаем формат с начальной 8:
    # 87001234567 -> 77001234567
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]

    # Номер должен содержать ровно 11 цифр
    # и начинаться с +7.
    if len(digits) != 11 or not digits.startswith("7"):
        raise forms.ValidationError("Please enter a valid Kazakhstan phone number.")

    # Казахстан использует диапазоны +7 0, +7 6 и +7 7.
    if digits[1] not in {"0", "6", "7"}:
        raise forms.ValidationError("Please enter a valid Kazakhstan phone number.")

    # Запрещаем буквы.
    if re.search(r"[A-Za-zА-Яа-я]", value):
        raise forms.ValidationError(
            "Phone number must contain only numbers and phone symbols."
        )


class ParticipantForm(forms.ModelForm):
    birth_day = forms.IntegerField(
        min_value=1,
        max_value=31,
        label="Day",
        widget=forms.NumberInput(
            attrs={
                "placeholder": "DD",
                "min": 1,
                "max": 31,
            }
        ),
    )

    birth_month = forms.IntegerField(
        min_value=1,
        max_value=12,
        label="Month",
        widget=forms.NumberInput(
            attrs={
                "placeholder": "MM",
                "min": 1,
                "max": 12,
            }
        ),
    )

    birth_year = forms.IntegerField(
        min_value=1900,
        max_value=date.today().year,
        label="Year",
        widget=forms.NumberInput(
            attrs={
                "placeholder": "YYYY",
                "min": 1900,
                "max": date.today().year,
            }
        ),
    )

    class Meta:
        model = Participant
        fields = ["full_name", "phone"]
        widgets = {
            "phone": forms.TextInput(
                attrs={
                    "placeholder": "+7 700 123 45 67",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        validate_phone(phone)

        digits = re.sub(r"\D", "", phone)

        if digits.startswith("8"):
            digits = "7" + digits[1:]

        return f"+{digits}"

    def clean(self):
        cleaned_data = super().clean()

        day = cleaned_data.get("birth_day")
        month = cleaned_data.get("birth_month")
        year = cleaned_data.get("birth_year")

        if day and month and year:
            try:
                birth_date = date(year, month, day)
            except ValueError:
                raise forms.ValidationError("Please enter a valid date of birth.")

            if birth_date > date.today():
                raise forms.ValidationError("Date of birth cannot be in the future.")

            cleaned_data["birth_date"] = birth_date

        return cleaned_data

    def save(self, commit=True):
        participant = super().save(commit=False)

        participant.birth_date = self.cleaned_data["birth_date"]

        if commit:
            participant.save()

        return participant
