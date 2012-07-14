from gcm import gcm

def push(msg):
    data = {"msg": msg}
    return gcm.GCM("AIzaSyCvogFVmhjneONn0F_-wBirq2q7wbqAe7g").json_request(
        registration_ids=["APA91bEa4qAO4t35CZc6oQm1oo22qqbpv7uacfmhVtHmVAKS9DaXRBj3tAX_cfno5321rs-d-JxRG9Nsni6Xj8KdFH7L2BHgWBdalKfiQ2Mhr_t44GPQFZUPVlxL0W-u1InWxYC1Z8TTHswPNXvvxn0a6BXyGpdPhQ"],
        data=data
    )