"""
Product intelligence router
"""
from fastapi import APIRouter, HTTPException, status, Depends
import json
from ..schemas.product_schemas import ProductResponse, ProductRuleUpdate
from ..models.database import db
from ..middleware.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
async def get_products(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all products with their inference rules
    
    Requires authentication
    """
    conn = db.get_connection()
    conn.row_factory = None
    c = conn.cursor()
    
    c.execute('''
        SELECT code, name, category, base_confidence_rules,
               primary_keywords, secondary_keywords, negative_keywords
        FROM products
        ORDER BY category, name
    ''')
    
    rows = c.fetchall()
    conn.close()
    
    products = []
    for row in rows:
        try:
            products.append(ProductResponse(
                code=row[0],
                name=row[1],
                category=row[2],
                baseConfidenceRules=json.loads(row[3]) if row[3] else {},
                primaryKeywords=json.loads(row[4]) if row[4] else [],
                secondaryKeywords=json.loads(row[5]) if row[5] else [],
                negativeKeywords=json.loads(row[6]) if row[6] else []
            ))
        except Exception as e:
            print(f"Error parsing product {row[0]}: {e}")
            continue
    
    return products


@router.put("/{product_code}/rules")
async def update_product_rules(
    product_code: str,
    rules: ProductRuleUpdate,
    current_user: dict = Depends(require_roles(['ADMIN']))
):
    """
    Update product inference rules (admin only)
    
    Requires ADMIN role
    """
    conn = db.get_connection()
    c = conn.cursor()
    
    # Check if product exists
    c.execute('SELECT id FROM products WHERE code = ?', (product_code,))
    if not c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product {product_code} not found"
        )
    
    # Build update query
    updates = []
    params = []
    
    if rules.baseConfidenceRules is not None:
        updates.append('base_confidence_rules = ?')
        params.append(json.dumps(rules.baseConfidenceRules))
    
    if rules.primaryKeywords is not None:
        updates.append('primary_keywords = ?')
        params.append(json.dumps(rules.primaryKeywords))
    
    if rules.secondaryKeywords is not None:
        updates.append('secondary_keywords = ?')
        params.append(json.dumps(rules.secondaryKeywords))
    
    if rules.negativeKeywords is not None:
        updates.append('negative_keywords = ?')
        params.append(json.dumps(rules.negativeKeywords))
    
    if not updates:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No updates provided"
        )
    
    # Add metadata
    from datetime import datetime
    updates.append('updated_at = ?')
    params.append(datetime.now().isoformat())
    updates.append('updated_by = ?')
    params.append(current_user['id'])
    
    # Execute update
    params.append(product_code)
    query = f"UPDATE products SET {', '.join(updates)} WHERE code = ?"
    c.execute(query, params)
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "productCode": product_code,
        "message": "Product rules updated successfully"
    }
