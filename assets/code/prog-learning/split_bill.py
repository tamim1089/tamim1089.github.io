def split_bill(total, people):
    share = round(total / people, 2)
    return [share] * people
