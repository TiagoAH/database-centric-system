-- FUNCTION: public.create_payment_on_appointment()

-- DROP FUNCTION IF EXISTS public.create_payment_on_appointment();

CREATE OR REPLACE FUNCTION public.create_payment_on_appointment()
    RETURNS trigger
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE NOT LEAKPROOF
AS $BODY$
DECLARE
    new_payment_id INTEGER;
BEGIN
    -- Insere um novo pagamento associado ao service_billing recém-criado
    INSERT INTO payment (amount, ispaid, service_billing_id, amout_payed, time_payed)
    VALUES (50, FALSE, NEW.service_billing_id, 0, NULL)
    RETURNING id INTO new_payment_id;

    RETURN NEW;
END;
$BODY$;

ALTER FUNCTION public.create_payment_on_appointment()
    OWNER TO postgres;

CREATE TRIGGER after_appointment_insert
AFTER INSERT ON appointment
FOR EACH ROW
EXECUTE FUNCTION create_payment_on_appointment();