# How to run

## FastAPI command

To run the API locally, you can run the following commands from repository root:

```
pip3 install -r requirements.txt
fastapi run app/main.py --port 8888
```

## Docker

To run the API through a Docker container, you can run the following command from repository root:

```
docker build -t powerplant-project .
docker run -p 8888:8888 powerplant-project
```

-----

Example of a test call using payload1.json

```
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{ "load": 480, "fuels": { "gas(euro/MWh)": 13.4, "kerosine(euro/MWh)": 50.8, "co2(euro/ton)": 20, "wind(%)": 60 }, "powerplants": [ { "name": "gasfiredbig1", "type": "gasfired", "efficiency": 0.53, "pmin": 100, "pmax": 460 }, { "name": "gasfiredbig2", "type": "gasfired", "efficiency": 0.53, "pmin": 100, "pmax": 460 }, { "name": "gasfiredsomewhatsmaller", "type": "gasfired", "efficiency": 0.37, "pmin": 40, "pmax": 210 }, { "name": "tj1", "type": "turbojet", "efficiency": 0.3, "pmin": 0, "pmax": 16 }, { "name": "windpark1", "type": "windturbine", "efficiency": 1, "pmin": 0, "pmax": 150 }, { "name": "windpark2", "type": "windturbine", "efficiency": 1, "pmin": 0, "pmax": 36 } ] }' \
  http://localhost:8888/productionplan
```

# What I focussed

- Create an API that accepts a payload with the required format.
- Implement an algorithm that always gives the best solution for them (or at least a solution), having into account possible edges with different problem data.
- Return a production plan with the required format.

# Aspects to improve

- Unit tests.
- Documentation and docstrings explaining parameters and return and its types + use key parameters to improve readability when needed. I just wrote some basic docstrings to explain the sense of each method.
- Create a better-organized class structures to split responsibilities. For example divide the payload processer and the algorithm into 2 different classes. This way, we could have an algorithm family and strategy pattern could be implemented.
- Better input data validation + when the input data is wrong, return a message specifying which of the data is wrong.
