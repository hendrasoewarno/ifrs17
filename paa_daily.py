'''
IFRS 17 using Premium Allocation Approach (PAA)
- General Insurance (Car, Travel, Property, Liability)

Validation:
1. Coverage period is 1 year or less, or
2. PAA would produce a result that is not materially different form the General Measurement Model (GMM)

Pengakuan Revenue dan Biaya adalah berdasarkan selisih hari, hal ini
dilakukan untuk mengantisipasi kontrak yang dimulai dan berakhir tidak
pada awal dan akhir bulan.

Pendekatan harian juga memberi manfaat untuk kontrak jangka pendek seperti asuransi Travel.
'''

from datetime import datetime, timedelta

def days_in_coverage(str_from_date, str_end_date):
    start_date = datetime.strptime(str_from_date, "%Y%m%d")
    end_date = datetime.strptime(str_end_date, "%Y%m%d")
    delta = (end_date - start_date).days + 1  # Include both start and end dates
    return delta

def prorated_months(str_from_date, str_end_date, str_current_date):
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
        if running_date < current_date:
            periods["last_periods"] += 1.0
        elif running_date == current_date:
            periods["periods"] += 1.0  # include current day as part of earned
        else:
            periods["next_periods"] += 1.0

    periods["periods"] += periods["last_periods"]
    periods["last_periods"] = 0.0  # Optional: combine into periods if no need to split further

    return periods

def LRC_upfront_prorated(premium, acquisition_cost, str_from_date, str_end_date, str_current_date, claim=0):
    sp = prorated_months(str_from_date, str_end_date, str_current_date)
    num_of_days = days_in_coverage(str_from_date, str_end_date)

    return {
        "Revenue Recognized": round(premium * sp["periods"] / num_of_days, 2),
        "LRC (Unearned Premium)": round(premium * sp["next_periods"] / num_of_days, 2),
        "Deferred Acquisition Cost": round(acquisition_cost * (sp["periods"] + sp["next_periods"]) / num_of_days, 2),
        "Insurance Service Expense": round(acquisition_cost * sp["periods"] / num_of_days, 2),
        "Insurance Service Expense vs LIC": claim
    }

# Contoh pemakaian
# premium = $1200
# acquisition_cost = $200
# start coverage date = 1 Jan 2025
# end coverage date = 30 Jun 2025
# tanggal akhir pelaporan = 31 Maret 2025
# tidak ada klaim yang tercatat dalam periode pelaporan
LRC = LRC_upfront_prorated(1200, 200, '20250101', '20250630', '20250331', 0)
print(LRC)
