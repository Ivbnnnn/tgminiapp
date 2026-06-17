from datetime import date
from decimal import Decimal


def calculate_full_years(start_date: date) -> int:
    today = date.today()

    years = today.year - start_date.year

    if (today.month, today.day) < (start_date.month, start_date.day):
        years -= 1

    return years


def calculate_k_power(power_hp: int) -> Decimal:
    if power_hp <=50: return Decimal(0.6)
    if 51<=power_hp <=70: return Decimal(1.0)
    if 71<=power_hp <=100: return Decimal(1.1)
    if 101<=power_hp <=120: return Decimal(1.2)
    if 121<=power_hp <=150: return Decimal(1.4)
    if power_hp > 150: return Decimal(1.6)


def calculate_k_use_period(use_period: int) -> Decimal:
    if use_period == 3: return Decimal(0.50)
    if use_period == 4: return Decimal(0.60)
    if use_period == 5: return Decimal(0.65)
    if use_period == 6: return Decimal(0.70)
    if use_period == 7: return Decimal(0.80)
    if use_period == 8: return Decimal(0.90)
    if use_period == 9: return Decimal(0.95)
    if use_period == 10: return Decimal(1.0)
    if use_period == 11: return Decimal(1.0)
    if use_period == 12: return Decimal(1.0)
    else:
        raise ValueError("Неверный срок use_period")


def calculate_k_region(city: str) -> Decimal:
    if "Москва" in city: return Decimal(1.8)
    elif "Санкт-Петербург" in city: return Decimal(1.6)
    elif "Казань" in city: return Decimal(1.5)
    else: return Decimal(1.0)

def calculate_k_age_exp(age: int, exp: int) -> Decimal:
    if 18 <= age <= 21:
        if exp == 0:
            return Decimal("2.27")
        if exp == 1:
            return Decimal("1.92")
        if exp == 2:
            return Decimal("1.84")
        if 3 <= exp <= 4:
            return Decimal("1.65")
        if 5 <= exp <= 6:
            return Decimal("1.62")

    if 22 <= age <= 24:
        if exp == 0:
            return Decimal("1.88")
        if exp == 1:
            return Decimal("1.72")
        if exp == 2:
            return Decimal("1.71")
        if 3 <= exp <= 4:
            return Decimal("1.13")
        if 5 <= exp <= 6:
            return Decimal("1.10")
        if 7 <= exp <= 9:
            return Decimal("1.09")

    if 25 <= age <= 29:
        if exp == 0:
            return Decimal("1.72")
        if exp == 1:
            return Decimal("1.60")
        if exp == 2:
            return Decimal("1.54")
        if 3 <= exp <= 4:
            return Decimal("1.09")
        if 5 <= exp <= 6:
            return Decimal("1.08")
        if 7 <= exp <= 9:
            return Decimal("1.07")
        if 10 <= exp <= 14:
            return Decimal("1.02")

    if 30 <= age <= 34:
        if exp == 0:
            return Decimal("1.56")
        if exp == 1:
            return Decimal("1.50")
        if exp == 2:
            return Decimal("1.48")
        if 3 <= exp <= 4:
            return Decimal("1.05")
        if 5 <= exp <= 6:
            return Decimal("1.04")
        if 7 <= exp <= 9:
            return Decimal("1.01")
        if 10 <= exp <= 14:
            return Decimal("0.97")
        if exp >= 15:
            return Decimal("0.95")

    if 35 <= age <= 39:
        if exp == 0:
            return Decimal("1.54")
        if exp == 1:
            return Decimal("1.47")
        if exp == 2:
            return Decimal("1.46")
        if 3 <= exp <= 4:
            return Decimal("1.00")
        if 5 <= exp <= 6:
            return Decimal("0.97")
        if 7 <= exp <= 9:
            return Decimal("0.95")
        if 10 <= exp <= 14:
            return Decimal("0.94")
        if exp >= 15:
            return Decimal("0.93")

    if 40 <= age <= 49:
        if exp == 0:
            return Decimal("1.50")
        if exp == 1:
            return Decimal("1.44")
        if exp == 2:
            return Decimal("1.43")
        if 3 <= exp <= 4:
            return Decimal("0.96")
        if 5 <= exp <= 6:
            return Decimal("0.95")
        if 7 <= exp <= 9:
            return Decimal("0.94")
        if 10 <= exp <= 14:
            return Decimal("0.93")
        if exp >= 15:
            return Decimal("0.91")

    if 50 <= age <= 59:
        if exp == 0:
            return Decimal("1.46")
        if exp == 1:
            return Decimal("1.40")
        if exp == 2:
            return Decimal("1.39")
        if 3 <= exp <= 4:
            return Decimal("0.93")
        if 5 <= exp <= 6:
            return Decimal("0.92")
        if 7 <= exp <= 9:
            return Decimal("0.91")
        if 10 <= exp <= 14:
            return Decimal("0.90")
        if exp >= 15:
            return Decimal("0.86")

    if age >= 60:
        if exp == 0:
            return Decimal("1.43")
        if exp == 1:
            return Decimal("1.36")
        if exp == 2:
            return Decimal("1.35")
        if 3 <= exp <= 4:
            return Decimal("0.91")
        if 5 <= exp <= 6:
            return Decimal("0.90")
        if 7 <= exp <= 9:
            return Decimal("0.89")
        if 10 <= exp <= 14:
            return Decimal("0.88")
        if exp >= 15:
            return Decimal("0.83")

    raise ValueError("Invalid age or experience for KVS")