import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def validate_product(self, product_id, auth_header):
        try:
            url = f"http://product_service:8000/api/products/{product_id}/"
            headers = {
                'Authorization': auth_header,
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException:
            return None

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate product exists and get its details
        product_data = self.validate_product(
            product_id, 
            request.headers.get('Authorization')
        )

        if not product_data:
            return Response(
                {'error': 'Product not found or service unavailable'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart, _ = Cart.objects.get_or_create(user_id=user_id)
            
            # Check if product already exists in cart
            existing_item = CartItem.objects.filter(
                cart=cart,
                product_id=product_id
            ).first()

            # Always use price from product service
            current_price = product_data['price']

            if existing_item:
                # Update quantity and ensure price is current
                existing_item.quantity += quantity
                existing_item.price = current_price  # Update to current price
                existing_item.save()
                serializer = CartItemSerializer(existing_item)
            else:
                cart_item = CartItem.objects.create(
                    cart=cart,
                    product_id=product_id,
                    quantity=quantity,
                    price=current_price  # Use price from product service
                )
                serializer = CartItemSerializer(cart_item)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = Cart.objects.get(user_id=user_id)
            cart_item = CartItem.objects.filter(
                cart=cart,
                product_id=product_id
            ).first()

            if not cart_item:
                return Response(
                    {'error': 'Product not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )

            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def increase_quantity(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = Cart.objects.get(user_id=user_id)
            cart_item = CartItem.objects.filter(
                cart=cart,
                product_id=product_id
            ).first()

            if not cart_item:
                return Response(
                    {'error': 'Product not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Validate product still exists and get current price
            product_data = self.validate_product(
                product_id, 
                request.headers.get('Authorization')
            )

            if not product_data:
                return Response(
                    {'error': 'Product not found or service unavailable'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cart_item.quantity += 1
            cart_item.price = product_data['price']  # Update to current price
            cart_item.save()
            
            return Response(CartItemSerializer(cart_item).data)

        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def decrease_quantity(self, request):
        user_id = request.user.id
        product_id = request.data.get('product_id')

        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart = Cart.objects.get(user_id=user_id)
            cart_item = CartItem.objects.filter(
                cart=cart,
                product_id=product_id
            ).first()

            if not cart_item:
                return Response(
                    {'error': 'Product not found in cart'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if cart_item.quantity <= 1:
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                cart_item.quantity -= 1
                cart_item.save()
                return Response(CartItemSerializer(cart_item).data)

        except Cart.DoesNotExist:
            return Response(
                {'error': 'Cart not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )