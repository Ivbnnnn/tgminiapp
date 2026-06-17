from datetime import date
from app.utils.calculation_helpers import (
    calculate_full_years,
    calculate_k_age_exp,
    calculate_k_power,
    calculate_k_region,
    calculate_k_use_period
    )
from decimal import Decimal

def make_policy_price_list(
        driver:dict,
        companies:dict,
        vehicle_and_sts:dict,
        person_and_address:dict,
        use_period:int,
        BASE_PRICE:int
) -> Decimal:
    
    birthdate = driver["birthdate"]
    license_issue_date = driver["license_issue_date"]
    if isinstance(birthdate, str):
        birthdate = date.fromisoformat(birthdate)

    if isinstance(license_issue_date, str):
        license_issue_date = date.fromisoformat(license_issue_date)
    age = calculate_full_years(birthdate)
    exp = calculate_full_years(license_issue_date)

    k_age_exp = calculate_k_age_exp(age, exp)

    power_hp = vehicle_and_sts["power_hp"]

    k_power = calculate_k_power(power_hp=power_hp)

    kbm = Decimal(str(driver["kbm"]))

    city = person_and_address["addresses"][0]["city"]

    k_region = calculate_k_region(city=city)

    k_multiple_osago = Decimal(1.0)

    k_use_period = calculate_k_use_period(use_period=use_period)

    

    result = []

    #расчет по команиям + привести все типы к Decimal
    for company in companies:
        policy_price = Decimal(str(BASE_PRICE)) * k_age_exp * k_power * kbm * k_region * k_multiple_osago * k_use_period * Decimal(str(company["koef"]))
        row = {
            "id":company["id"],
            "name":company["name"],
            "commission_percent":company["commission_percent"],
            "policy_price": float(policy_price.quantize(Decimal("0.01")))
        }
        result.append(row)
    return result



