List of not linked resources
----------------------------

To get list of GitLab resources that can be linked to NodeConductor - issue GET request against
**/api/gitlab/<service_uuid>/link/**.

Available filters:

?resource_type - name of gilab resource: 'project' or 'group'. Optional, if not defined - endpoint will return all
                 available resources.


Link GitLab resource to NodeConductor
-------------------------------------

To link GitLab resource to NodeConductor - issue POST request against **/api/gitlab/<service_uuid>/link/**.

Request example:

.. code-block:: http

    POST /api/gitlab/<service_uuid>/link/ HTTP/1.1
    Content-Type: application/json
    Accept: application/json
    Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
    Host: example.com

    {
        "project": "http://example.com/api/projects/73c7807a577145f5a3a3f8d9ecc1f2ac/",
        "backend_id": "45",
        "type": "project"
    }


Project commits count
---------------------

To get GitLab project commits count - check project "commit_count" quota. Quota history can be used as commits count
historical data. Look "Quotas" section for more details.
