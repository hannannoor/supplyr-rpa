
DROP DATABASE IF EXISTS supplyr;
CREATE DATABASE supplyr;
USE supplyr;

-- ------------------------------------------------------------
-- Suppliers (10 suppliers, some with missing data)
-- ------------------------------------------------------------
CREATE TABLE suppliers (
    supplier_id     INT PRIMARY KEY,
    supplier_name   VARCHAR(100) NOT NULL,
    supplier_email  VARCHAR(120),
    delivery_days   INT
);

INSERT INTO suppliers VALUES
(1,  'FreshFarm Wholesale',      'orders@freshfarm.example.com',    3),
(2,  'PrimeSnacks Pte Ltd',      'sales@primesnacks.example.com',   5),
(3,  'DailyGoods Supply Co',     'reorder@dailygoods.example.com',  2),
(4,  'ValueMart Distributors',    NULL,                              4),
(5,  'QuickStock Traders',       'hello@quickstock.example.com',    7),
(6,  'MegaBulk Supplies',        'orders@megabulk.example.com',     1),
(7,  'IslandFresh Pte Ltd',      'supply@islandfresh.example.com',  3),
(8,  'BudgetWhole Distributors',  NULL,                              6),
(9,  'TopShelf Trading Co',      'sales@topshelf.example.com',      4),
(10, 'EcoGoods Wholesale',       'eco@ecogoods.example.com',        5);

-- ------------------------------------------------------------
-- Products (50 products with reorder_status column)
-- ------------------------------------------------------------
CREATE TABLE products (
    product_id      INT PRIMARY KEY,
    product_name    VARCHAR(100) NOT NULL,
    current_stock   INT,
    minimum_stock   INT,
    reorder_qty     INT,
    unit_price      DECIMAL(10,2),
    reorder_status  VARCHAR(30) DEFAULT 'OK'
);

INSERT INTO products (product_id, product_name, current_stock, minimum_stock, reorder_qty, unit_price) VALUES
-- LOW STOCK items (20)
(101, 'Instant Noodles (carton)',        12,  40,  60,  8.50),
(102, 'Canned Tuna (24 tin)',             5,  30,  50, 15.00),
(103, 'Rice 5kg bag',                    35,  60,  30, 12.90),
(104, 'Biscuits Assorted (box)',          0,  20,  35,  9.40),
(105, 'Detergent Powder 3kg',           18,  30,  25, 11.20),
(106, 'Eggs (tray of 30)',               8,  35,  50,  6.10),
(107, 'Coffee Powder 500g',             28,  30,  20, 13.50),
(108, 'Cooking Oil 5L',                  3,  25,  40,  9.80),
(109, 'Soy Sauce 1L',                   10,  20,  30,  4.50),
(110, 'Canned Sardines (12 tin)',         2,  15,  25, 12.30),
(111, 'Paper Towels (6 roll)',           14,  25,  20,  5.90),
(112, 'Dishwashing Liquid 1L',           6,  20,  30,  3.80),
(113, 'Trash Bags (50 pack)',             1,  10,  20,  7.20),
(114, 'Condensed Milk (24 tin)',         22,  40,  35, 16.50),
(115, 'Frozen Chicken Wings 1kg',         0,  30,  40, 11.00),
(116, 'Tomato Ketchup 500ml',           15,  20,  25,  3.20),
(117, 'Chilli Sauce 500ml',             11,  18,  20,  2.90),
(118, 'Laundry Softener 2L',             7,  15,  25,  8.60),
(119, 'Hand Soap 500ml',                 4,  20,  30,  4.10),
(120, 'Face Tissue Box (5 pack)',         9,  25,  20,  6.40),
-- OK STOCK items (20)
(121, 'Bottled Water 500ml (24pk)',      90,  50,  40,  4.20),
(122, 'Cooking Oil 2L',                  70,  25,  20,  6.75),
(123, 'Soft Drink Cola (12pk)',          45,  45,  30,  5.60),
(124, 'Shampoo 1L',                      55,  40,  30,  8.90),
(125, 'Toothpaste 200g',                60,  30,  25,  3.50),
(126, 'Milo Powder 1kg',                80,  35,  40, 10.20),
(127, 'Peanut Butter 500g',             40,  20,  15,  7.30),
(128, 'Spaghetti 500g (10 pack)',        35,  30,  20,  5.10),
(129, 'Mineral Water 1.5L (12pk)',       75,  40,  30,  6.00),
(130, 'Cereal Box 500g',                50,  25,  20,  9.80),
(131, 'Butter 250g',                     42,  20,  15,  4.50),
(132, 'Flour 1kg',                       38,  15,  25,  2.80),
(133, 'Sugar 1kg',                       55,  30,  20,  3.10),
(134, 'Vinegar 500ml',                   30,  10,  15,  2.20),
(135, 'Canned Corn (12 tin)',            28,  15,  20,  8.40),
(136, 'Olive Oil 500ml',                45,  20,  15, 14.50),
(137, 'Tea Bags (100 pack)',             60,  25,  30,  5.70),
(138, 'Aluminum Foil 30m',              33,  15,  20,  4.90),
(139, 'Plastic Wrap 100m',              40,  20,  15,  3.60),
(140, 'Battery AA (8 pack)',             25,  10,  20,  7.80),
-- BAD DATA rows (5) - test row-level validation
(141, 'Toilet Paper (12 roll)',          22, NULL,  40,  7.80),
(142, 'Hand Sanitizer 500ml',          NULL,   20,  30,  5.50),
(143, 'Bleach 2L',                       15, NULL,  20,  4.30),
(144, 'Wet Wipes (80 pack)',           NULL, NULL,  25,  3.90),
(145, 'Air Freshener 300ml',            10, NULL,  15,  6.20),
-- EDGE CASES (5)
(146, 'Mosquito Coil (10 pack)',         20,  20,  15,  3.40),
(147, 'Matches (12 box)',               100,   5,  10,  1.20),
(148, 'Candles (6 pack)',                 1,   1,  10,  2.50),
(149, 'Rubber Gloves (pair)',            50,  50,  20,  4.80),
(150, 'Ziplock Bags (100 pack)',          0,   0,  25,  5.30);

-- ------------------------------------------------------------
-- Product-Supplier linking table (many-to-many)
-- ------------------------------------------------------------
CREATE TABLE product_suppliers (
    product_id      INT,
    supplier_id     INT,
    supplier_price  DECIMAL(10,2),
    available_qty   INT,
    PRIMARY KEY (product_id, supplier_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id)
);

INSERT INTO product_suppliers VALUES
(101, 2,  8.50,  300), (101, 6,  9.20, 1000), (101, 3,  7.80,  800),
(102, 3, 15.00,  800), (102, 7, 14.20,  600), (102, 9, 15.80,  450),
(103, 1, 12.90,  500), (103, 6, 13.50, 1000),
(104, 4,  9.40,  400), (104, 8, 10.00,  350),
(105, 5, 11.20,  150), (105, 9, 10.80,  450), (105, 10, 11.50, 200),
(106, 1,  6.10,  500), (106, 7,  6.50,  600),
(107, 2, 13.50,  300), (107, 10, 12.90, 200),
(108, 6,  9.80, 1000), (108, 3, 10.20,  800), (108, 1,  9.50,  500),
(109, 3,  4.50,  800), (109, 9,  4.80,  450),
(110, 7, 12.30,  600), (110, 2, 12.80,  300),
(111, 9,  5.90,  450), (111, 6,  5.50, 1000),
(112, 10, 3.80,  200), (112, 3,  3.50,  800), (112, 5,  4.00,  150),
(113, 6,  7.20, 1000), (113, 9,  7.50,  450),
(114, 2, 16.50,  300), (114, 7, 16.00,  600),
(115, 8, 11.00,  350), (115, 4, 11.80,  400),
(116, 3,  3.20,  800), (116, 10, 3.40,  200),
(117, 3,  2.90,  800), (117, 1,  3.10,  500),
(118, 9,  8.60,  450), (118, 5,  8.90,  150),
(119, 7,  4.10,  600), (119, 3,  3.90,  800), (119, 10, 4.30,  200),
(120, 10, 6.40,  200), (120, 6,  6.00, 1000);

-- Verify:
SELECT 'Total products' AS label, COUNT(*) AS count FROM products
UNION ALL
SELECT 'Low stock items', COUNT(*) FROM products WHERE current_stock IS NOT NULL AND minimum_stock IS NOT NULL AND current_stock < minimum_stock
UNION ALL
SELECT 'OK stock items', COUNT(*) FROM products WHERE current_stock IS NOT NULL AND minimum_stock IS NOT NULL AND current_stock >= minimum_stock
UNION ALL
SELECT 'Bad data rows', COUNT(*) FROM products WHERE current_stock IS NULL OR minimum_stock IS NULL
UNION ALL
SELECT 'Product-supplier links', COUNT(*) FROM product_suppliers;
