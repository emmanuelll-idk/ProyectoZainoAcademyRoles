
CREATE DATABASE IF NOT EXISTS pos_venta;
USE pos_venta;

-- Tabla ventas
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente VARCHAR(100) NOT NULL,
    producto VARCHAR(100) NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) GENERATED ALWAYS AS (cantidad * precio) STORED,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Datos de ejemplo
INSERT INTO ventas (cliente, producto, cantidad, precio)
VALUES
('Juan Pérez', 'Vitamina C', 2, 15000),
('María Gómez', 'Té Verde', 1, 12000),
('Carlos Ruiz', 'Colágeno', 3, 25000);
