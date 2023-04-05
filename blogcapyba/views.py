
from rest_framework.response import Response
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import BasePermission
from rest_framework.permissions import (
    IsAuthenticated,
)
from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from.serializers import PostSerializer
from .models import Post



    
class PostListView(APIView):

    
    @api_view(http_method_names=["GET"])
    @permission_classes([IsAuthenticated])
    def get(self, request):
       
        page_number = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search_query = request.query_params.get('search', '')
        order_by = request.query_params.get('order_by', 'id')
        is_published= request.query_params.get('is_published', None)

     
        queryset = Post.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query)).order_by(order_by)

        if is_published is not None:
            queryset = queryset.filter(is_published=is_published)
       
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)

       
        serializer = PostSerializer(page, many=True)
        response_data = {
            'total_results': paginator.count,
            'total_pages': paginator.num_pages,
            'results': serializer.data
        }
        return Response(response_data)

class IsVerified(BasePermission):
    def has_permission(self, request,view):
        return request.user.is_authenticated and request.user.is_verified
    
class PostViewRestrict(APIView):

    
    @api_view(http_method_names=["GET"])
    @permission_classes([IsVerified])
    def get(self, request):
       
        page_number = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 10))
        search_query = request.query_params.get('search', '')
        order_by = request.query_params.get('order_by', 'id')
        is_published = request.query_params.get('is_published', None)

     
        queryset = Post.objects.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query)).order_by(order_by)
     
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published)

        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(page_number)

       
        serializer = PostSerializer(page, many=True)
        response_data = {
            'total_results': paginator.count,
            'total_pages': paginator.num_pages,
            'results': serializer.data
        }
        return Response(response_data)


