'''
IFRS 17 using General Measurement Model (GMM)
a.k.a. Full Measurement Model (FMM)
a.k.a. Building Block Approach (BAA)
- Kontrak Jangka Panjang (Asuransi Jiwa, Kesehatan Jangka Panjang)

Validation:
1. Coverage period lebih dari satu tahun
2. PAA menghasilkan hasil yang secara material berbeda dengan GMM, atau
3. Kontrak tidak memenuhi syarat sebagai kontrak asuransi jangka pendek, atau
4. Kontrak termasuk Asuransi jiwa jangka panjang, Asuransi kesehatan jangka panjang, Asuransi dengan partisipas investasi (jika tidak memenuhi kriteria VFA)

Key Features:
1. Profit is pread over the coverage period
2. Simplified treatmetn of acquistion costs
3. Discounting is optional (only required if impact is material)

Pengakuan Revenue dan Biaya adalah berdasarkan selisih hari, hal ini
dilakukan untuk mengantisipasi kontrak yang dimulai dan berakhir tidak
pada awal dan akhir bulan.

Pendekatan harian juga memberi manfaat untuk kontrak jangka pendek seperti asuransi Travel.
'''

from datetime import datetime, timedelta

'''
discounting is only required if the effect is material
- Liablility for incurred Claims (LIC)
- Risk Adjustment (RA)
- Expected Future Claims

due to longer claim settlements or delayed payment
'''
def apply_discounting(value, discount_rate, duration_in_days):
    """
    Applies time value of money discounting to a future value.
    Arguments:
        value (float): undiscounted amount
        discount_rate (float): annual discount rate, e.g., 0.05 for 5%
        duration_in_days (int): time until payment
    Returns:
        float: present value
    """
    return value / ((1 + discount_rate) ** (duration_in_days / 365))

def days_in_coverage(str_from_date, str_end_date):
    """
    Returns the number of days in the insurance coverage period (inclusive).
    """
    start_date = datetime.strptime(str_from_date, "%Y%m%d")
    end_date = datetime.strptime(str_end_date, "%Y%m%d")
    delta = (end_date - start_date).days + 1  # Include both start and end dates
    return delta

def prorated_days(str_from_date, str_end_date, str_current_date):
    start_date = datetime.strptime(str_from_date, "%Y%m%d")
    end_date = datetime.strptime(str_end_date, "%Y%m%d")
    current_date = datetime.strptime(str_current_date, "%Y%m%d")

    periods = {
        "last_periods": 0.0,
        "periods": 0.0,
        "next_periods": 0.0
    }

    num_of_days = days_in_coverage(str_from_date, str_end_date)

    for i in range(num_of_days):
        running_date = start_date + timedelta(days=i)
        #periode tahun lalu, jika kontrak lintas tahun
        if running_date.year < current_date.year:
            periods["last_periods"] += 1.0
        elif running_date <= current_date:
            periods["periods"] += 1.0  # include current day as part of earned
        else:
            periods["next_periods"] += 1.0

    return periods

def LRC_upfront_prorated(premium, acquisition_cost, str_from_date, str_end_date, str_current_date, claim=0, risk_adjustment=0, expected_future_claims=0):
    sp = prorated_days(str_from_date, str_end_date, str_current_date)
    num_of_days = days_in_coverage(str_from_date, str_end_date)
    
    #future
    unearned_premium = round(premium * sp["next_periods"] / num_of_days, 2)
    dac_remaining = round(acquisition_cost * sp["next_periods"] / num_of_days, 2)
    
    # Onerous contract test
    future_outflows = expected_future_claims + dac_remaining + risk_adjustment
    
    #onerous jika Future in flow < Future out flow
    is_onerous = unearned_premium < future_outflows
    loss_component = round(future_outflows - unearned_premium, 2) if is_onerous else 0.0    

    return {
        "Revenue Recognized (P&L)": round(premium * sp["periods"] / num_of_days, 2),
        "Unearned Premium (LRC)": unearned_premium,
        "Deferred Acquisition Cost (DAC)": round(acquisition_cost * (sp["periods"] + sp["next_periods"]) / num_of_days, 2),
        "Acquisition Cost Expense (P&L)": round(acquisition_cost * sp["periods"] / num_of_days, 2),
        "Insurance Service Expense vs Liability for Incurred Claims (LIC) + RA": claim + (risk_adjustment if risk_adjustment>0 else 0),
        "Risk Adjustment Relaease (P&L) vs Insurance Revenue": (-risk_adjustment if risk_adjustment<0 else 0),
        "Onerous": is_onerous,
        "Loss Component": loss_component
    }

# Contoh pemakaian
# premium = $1200
# acquisition_cost = $200
# start coverage date = 1 Jan 2025
# end coverage date = 30 Jun 2025
# tanggal akhir pelaporan = 31 Maret 2025
# klaim yang tercatat dalam periode tahun pelaporan = 1000
# risk adjusment dalam periode tahun pelaporan = 80
# expected future claims = 500
LRC = LRC_upfront_prorated(1200, 200, '20250101', '20250630', '20250331', 1000, 80,500)
#LRC = LRC_upfront_prorated(1200, 200, '20250101', '20250630', '20250331', discount_rate(1000, 0.05, 730), 80,500)
print(LRC)
