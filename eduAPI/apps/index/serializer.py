from rest_framework.serializers import ModelSerializer

from index.models import Banner, Nav


class BannerSerializer(ModelSerializer):
    class Meta:
        model = Banner
        fields = ['img', 'link']


class NavSerializer(ModelSerializer):
    class Meta:
        model = Nav
        fields = ['title', 'link', 'position', 'is_site']
