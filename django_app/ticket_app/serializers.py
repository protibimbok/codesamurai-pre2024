from rest_framework import serializers

class TicketPurchase(serializers.Serializer):
    wallet_id = serializers.IntegerField()
    time_after = serializers.CharField()
    station_from = serializers.IntegerField()
    station_to = serializers.IntegerField()
    


class PlanQuery(serializers.Serializer):
    
    fields = {
        'from': serializers.IntegerField(),
        'to': serializers.IntegerField(),
        'optimize': serializers.ChoiceField(choices=['cost', 'time']),
    }
    