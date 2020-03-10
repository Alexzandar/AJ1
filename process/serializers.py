from rest_framework import serializers

from masters.models import DestinationTools, DestinationFile


class APISerializer(serializers.Serializer):
    tool = serializers.CharField()
    destination_file = serializers.CharField()

    def validate_tool(self, value):
        try:
            tool = DestinationTools.objects.get(tool_short=value)
            return tool.tool_id
        except:
            raise serializers.ValidationError('Unable to get Tool.')

    def validate_destination_file(self, value):
        try:
            dest_file = DestinationFile.objects.get(dest_short=value)
            return dest_file.dest_file_id
        except:
            raise serializers.ValidationError('Unable to get Destination File.')
