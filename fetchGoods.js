const data = {
  "goods": [
    {
      "ID": 1,
      "Name": "Methylamine",
      "Category": "Chemicals",
      "Price": 5000.0,
      "StockQuantity": 10
    },
    {
      "ID": 2,
      "Name": "Hydrofluoric Acid",
      "Category": "Chemicals",
      "Price": 2000.0,
      "StockQuantity": 5
    },
    {
      "ID": 3,
      "Name": "Phenylacetone",
      "Category": "Chemicals",
      "Price": 7500.0,
      "StockQuantity": 3
    },
    {
      "ID": 4,
      "Name": "Acetone",
      "Category": "Chemicals",
      "Price": 50.0,
      "StockQuantity": 100
    },
    {
      "ID": 5,
      "Name": "Sulfuric Acid",
      "Category": "Chemicals",
      "Price": 100.0,
      "StockQuantity": 80
    },
    {
      "ID": 6,
      "Name": "Portable Lab Burner",
      "Category": "Equipment",
      "Price": 300.0,
      "StockQuantity": 15
    },
    {
      "ID": 7,
      "Name": "Glass Beakers Set",
      "Category": "Equipment",
      "Price": 150.0,
      "StockQuantity": 50
    },
    {
      "ID": 8,
      "Name": "Distillation Kit",
      "Category": "Equipment",
      "Price": 800.0,
      "StockQuantity": 5
    },
    {
      "ID": 9,
      "Name": "Pressure Cooker",
      "Category": "Equipment",
      "Price": 120.0,
      "StockQuantity": 20
    },
    {
      "ID": 10,
      "Name": "Digital Scale",
      "Category": "Equipment",
      "Price": 250.0,
      "StockQuantity": 10
    },
    {
      "ID": 11,
      "Name": "Hazmat Suit",
      "Category": "Protective Gear",
      "Price": 350.0,
      "StockQuantity": 20
    },
    {
      "ID": 12,
      "Name": "Respirator Mask",
      "Category": "Protective Gear",
      "Price": 80.0,
      "StockQuantity": 30
    },
    {
      "ID": 13,
      "Name": "Nitrile Gloves",
      "Category": "Protective Gear",
      "Price": 10.0,
      "StockQuantity": 200
    },
    {
      "ID": 14,
      "Name": "Safety Goggles",
      "Category": "Protective Gear",
      "Price": 15.0,
      "StockQuantity": 100
    },
    {
      "ID": 15,
      "Name": "Chemical Resistant Boots",
      "Category": "Protective Gear",
      "Price": 70.0,
      "StockQuantity": 25
    }
  ],
  "suppliers": [
    {
      "SupplierID": 1,
      "SupplierName": "Los Pollos Supplies",
      "ContactNumber": "555-1234"
    },
    {
      "SupplierID": 2,
      "SupplierName": "Gray Matter Chemicals",
      "ContactNumber": "555-5678"
    },
    {
      "SupplierID": 3,
      "SupplierName": "Saul Goodman Importers",
      "ContactNumber": "555-4321"
    },
    {
      "SupplierID": 4,
      "SupplierName": "Vamonos Pest Equipment",
      "ContactNumber": "555-8765"
    }
  ]
};


exports.handler = async function(event, context) {
    console.log('Function executed. Event:', JSON.stringify(event));

    try {
	console.log('Data available. Number of goods:', data.goods.length);

        return {
            statusCode: 200,
            body: JSON.stringify(data)
        };
    } catch (error) {
        console.error("Error in function:", error);
        return {
            statusCode: 500,
            body: JSON.stringify({ error: 'Function execution failed', details: error.message })
        };
    }
};
window.data = data;