Order list
----------

To get a list of plans, run GET against **/api/orders/** as authenticated user. Note that only customer owner can
see orders that are connected to his customer.


Create a new order
------------------

A new order can only be created by users with staff privilege (is_staff=True) or customer owners. Example of a
valid request:

.. code-block:: http

    POST /api/orders/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "customer": "http://example.com/api/customers/eb49e5a625f247299bfcf391146bb978/",
        "plan": "http://example.com/api/plans/494e623c83b9476bb5777b536c9d5a30/"
    }


Execute order
-------------

Order "execute" action is available only if payments dummy mode is enabled. Any processing order can be executed
with POST request against **/api/orders/<order_uuid>/execute/** without any additional data.
