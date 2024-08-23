@app.post("/exect-task/")
async def create_instance(request: schemas.Manageable, db: Session = Depends(get_db)):
    datos = {
        "id_adminis": None,
        "id_sensor": request.params["id_adminis"],
        "ag_name": "",
        "id_agent": request.id_agent,
        "oid": "",
        "adminis_name": (
            lambda x: (
                request.nametask
                if request.nametask != "Networktraffic"
                else request.nametask + request.params["num_interface"]
            )
        )(None),
        "timer": request.params["timer"],
    }

    feature = schemas.new_features(**datos)

    state = await activator_tasks(
        name=request.name, nametask=request.nametask, params=request.params
    )
    if state:
        crud.add_active_default(db=db, dates=request)
        if request.nametask == "Networktraffic":
            for i in range(0, 2):
                id_sensor = int(
                    str(request.params["id_adminis"])
                    + str(request.params["num_interface"])
                    + f"{i}"
                )
                feature.id_sensor = id_sensor
                feature.adminis_name = feature.adminis_name + (
                    lambda x: "IN" if i == 0 else "OUT"
                )(None)
                crud.new_feature(db=db, feature=feature)
        else:
            crud.new_feature(db=db, feature=feature)
    else:
        raise HTTPException(status_code=400, detail="Tarea no subida")
