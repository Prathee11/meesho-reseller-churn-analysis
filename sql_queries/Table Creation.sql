USE meesho_churn;
CREATE TABLE resellers_table (
  reseller_id VARCHAR(10),
  name VARCHAR(100),
  phone VARCHAR(20),
  signup_date DATE,
  state VARCHAR(50),
  city_tier INT,
  age_group VARCHAR(10),
  primary_category VARCHAR(20),
  monthly_gmv FLOAT,
  monthly_orders INT,
  avg_order_value FLOAT,
  return_rate FLOAT,
  support_tickets INT,
  whatsapp_active INT,
  tenure_days INT,
  days_since_last_order INT,
  churn_label INT
);