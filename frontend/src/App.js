import React, { Component } from "react";
import './App.css';
import "antd/dist/antd.css";

import axios from 'axios';

import CurrentPosition from './components/CurrentPosition/CurrentPosition.js'
import LocationsList from './components/LocationsList/LocationsList.js'

const ALL_COUNTRIES_API = 'http://0.0.0.0:8000/api/v1/countries/'
const LOCATIONS_WEATHER_API = 'http://0.0.0.0:8000/api/v1/locations/update_weather/'
const MY_WEATHER_API = 'http://0.0.0.0:8000/api/v1/weathers/current_weather/'
const MY_FORECAST_API = 'http://0.0.0.0:8000/api/v1/weathers/forecast_weather/'

class App extends Component {
  state = {
    currentLocation: null,
    currentLocationError: null,
    currentLocationWeatherInfo: null,
    currentLocationForecastInfo: null,
    locationsWeatherInfo: null,
    allCountriesInfo: null,
  }

  /**
    returns all countries from API for listing when adding new location
  */
  requestAllcountries = async () => {
    const allcountriesData = await axios.get(ALL_COUNTRIES_API)
    let allCountriesInfo = null
    if (allcountriesData && allcountriesData.status === 200) {
      allCountriesInfo = allcountriesData.data
    }
    this.setState({allCountriesInfo})
  }

  /**
    returns all locations weather from API
  */
  getLocationsWeather = async () => {
    const locationsWeatherData = await axios.get(
      LOCATIONS_WEATHER_API,
      {
        params : {
          dt: Math.floor(new Date().getTime() / 1000)
        }
      }
    )
    let locationsWeatherInfo = null
    if (locationsWeatherData && locationsWeatherData.status === 200) {
      locationsWeatherInfo = locationsWeatherData.data
    }
    this.setState({locationsWeatherInfo})
  }

  /**
    - callback function when getcurrentPosition successes
      - gets current location weather from API
      - gets current location forecast from API
  */
  currentPositionSuccess = async (pos) => {
    const coord = pos.coords;

    const currentWeatherData = await axios.get(
      MY_WEATHER_API,
      {
        params : {
          lat: coord.latitude,
          lon: coord.longitude,
          dt: Math.floor(new Date().getTime() / 1000)
        }
      }
    )
    let currentLocationWeatherInfo = null
    if (currentWeatherData && currentWeatherData.status === 200) {
      currentLocationWeatherInfo = currentWeatherData.data
    }

    const currentWeatherForecastData = await axios.get(
      MY_FORECAST_API,
      {
        params : {
          lat: coord.latitude,
          lon: coord.longitude,
        }
      }
    )
    let currentLocationForecastInfo = null
    if (currentWeatherForecastData && currentWeatherForecastData.status === 200) {
      currentLocationForecastInfo = currentWeatherForecastData.data
    }

    this.setState({
      currentLocation: {
        lat: coord.latitude,
        lon: coord.longitude,
      },
      currentLocationError: null,
      currentLocationWeatherInfo,
      currentLocationForecastInfo
    })
  }

  /**
    - callback function when getcurrentPosition fails
  */
  currentPositionError = (err) => {
    this.setState({
      currentLocationError: err,
    })
  }

  /**
    - returns current location and calls success and fail callbacks
  */
  getCurrentPosition = async () => {
    const options = {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    };

    navigator.geolocation.getCurrentPosition(
      this.currentPositionSuccess,
      this.currentPositionError,
      options
    );
  }

  /**
    - calls APIs for getting current location weather and forecast
  */
  requestLocationsWeatherAndForecast = () => {
    this.getCurrentPosition();
    this.getLocationsWeather();
  }

  /**
    - sets interval for every 1 min
  */
  componentDidMount() {
    this.requestLocationsWeatherAndForecast()
    this.locationIntervalId = setInterval(() => {
      this.requestLocationsWeatherAndForecast()
    }, 60000)
    this.requestAllcountries();
  }

  /**
    - kills interval
  */
  componentWillUnmount() {
    clearInterval(this.locationIntervalId)
  }

  render() {
    const {
      currentLocation,
      currentLocationError,
      currentLocationWeatherInfo,
      currentLocationForecastInfo,
      locationsWeatherInfo,
      allCountriesInfo
    } = this.state
    return (
      <div className="App">
        <CurrentPosition
          currentLocation={currentLocation}
          currentLocationError={currentLocationError}
          currentLocationWeatherInfo={currentLocationWeatherInfo}
          currentLocationForecastInfo={currentLocationForecastInfo}
        />
        <LocationsList
          locationsWeatherInfo={locationsWeatherInfo}
          allCountriesInfo={allCountriesInfo}
        />
      </div>
    );
  }
}

export default App;
