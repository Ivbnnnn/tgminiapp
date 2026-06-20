from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Response, UploadFile, status

from app.db.uow import UnitOfWork
from app.deps import get_current_seller, get_uow
from app.models.products import Product
from app.models.sellers import Seller
from app.schemas.product_photos import ProductPhotoCreate, ProductPhotoRead
from app.schemas.products import ProductCreate, ProductDetail, ProductFilters, ProductRead, ProductUpdate
from app.services.storage import object_storage


router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductDetail])
async def list_products(
    filters: ProductFilters = Depends(),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    uow: UnitOfWork = Depends(get_uow),
):
    return await uow.products.search(filters, limit=limit, offset=offset)


@router.get("/{product_id}", response_model=ProductDetail)
async def read_product(product_id: int, uow: UnitOfWork = Depends(get_uow)):
    product = await uow.products.read_detail(product_id)
    return _found(product)


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    seller: Seller = Depends(get_current_seller),
    uow: UnitOfWork = Depends(get_uow),
):
    return await uow.products.create_for_seller(
        data,
        seller,
    )


@router.patch("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    seller: Seller = Depends(get_current_seller),
    uow: UnitOfWork = Depends(get_uow),
):
    await _owned_product(product_id, seller, uow)
    return _found(await uow.products.update(product_id, data))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    seller: Seller = Depends(get_current_seller),
    uow: UnitOfWork = Depends(get_uow),
) -> Response:
    await _owned_product(product_id, seller, uow)
    for photo in await uow.product_photos.read_for_product(product_id):
        await object_storage.delete_by_url(photo.url)
    await uow.products.delete(product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{product_id}/photos",
    response_model=ProductPhotoRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_photo(
    product_id: int,
    position: int = Form(ge=1, le=4),
    file: UploadFile = File(),
    seller: Seller = Depends(get_current_seller),
    uow: UnitOfWork = Depends(get_uow),
):
    await _owned_product(product_id, seller, uow)
    existing = await uow.product_photos.read_for_product(product_id)
    if len(existing) >= 4 or any(photo.position == position for photo in existing):
        raise HTTPException(status_code=409, detail="Photo position is already occupied")
    try:
        url = await object_storage.upload_product_photo(product_id, file)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    photo = await uow.product_photos.insert(
        ProductPhotoCreate(product_id=product_id, url=url, position=position)
    )
    if photo is None:
        await object_storage.delete_by_url(url)
        raise HTTPException(status_code=500, detail="Could not save photo")
    return photo


@router.delete("/{product_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_photo(
    product_id: int,
    photo_id: int,
    seller: Seller = Depends(get_current_seller),
    uow: UnitOfWork = Depends(get_uow),
) -> Response:
    await _owned_product(product_id, seller, uow)
    photo = await uow.product_photos.read(photo_id)
    if photo is None or photo.product_id != product_id:
        raise HTTPException(status_code=404, detail="Photo not found")
    await uow.product_photos.delete(photo_id)
    await object_storage.delete_by_url(photo.url)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def _owned_product(product_id: int, seller: Seller, uow: UnitOfWork) -> Product:
    product = await uow.products.read(product_id)
    _found(product)
    if product.seller_id != seller.id and product.seller_telegram_id != seller.telegram_id:
        raise HTTPException(status_code=403, detail="Only the seller can modify this product")
    return product


def _found(product: Product | None) -> Product:
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
