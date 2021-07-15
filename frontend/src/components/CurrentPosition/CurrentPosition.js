import React, { Component } from "react";
import './CurrentPosition.css'

import WeatherForecast from "./components/WeatherForecast.js"

import { Typography, Skeleton } from "antd"

class Loading extends Component {
  render () {
    return (
      <div className="CurrentLocationMain">
        <div className="CurrentLocationWeather">
          <Skeleton.Input style={{ width: 350 }} active size={20} />
          <br/><br/>
          <Skeleton.Input style={{ width: 200 }} active size={20} />
          <br/><br/><br/>
          <Skeleton.Input style={{ width: 50 }} active size={20} />
          <br/><br/><br/>
          <Skeleton.Input style={{ width: 200 }} active size={20} />
        </div>
        <WeatherForecast/>
      </div>
    )
  }
}

export default class CurrentPosition extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const {
      currentLocationError,
      currentLocationWeatherInfo,
      currentLocationForecastInfo,
    } = this.props
    return (
      <div className="CurrentLocationMain">
        {currentLocationError ? <div>
          <span>
            {`${currentLocationError.code}: ${currentLocationError.message} `}<strong> Retry? </strong>
          </span>
        </div> : null}
        {currentLocationWeatherInfo ? <div>
          {/* <p>{JSON.stringify(currentLocationWeatherInfo)}</p> */}
          <div className="CurrentLocationWeather">
            <span>
              <Typography.Title level={2} className="Title">
                {`${currentLocationWeatherInfo.city}, ${currentLocationWeatherInfo.country} (${currentLocationWeatherInfo.country_code})`}
              </Typography.Title>
            </span>
            <small className="LastUpdate">{`Last update at ${new Date(currentLocationWeatherInfo.unix_last_update).toLocaleTimeString()}`}</small>
            <p className="MainTemp">{`${Math.round(currentLocationWeatherInfo.temperature)}˚`}</p>
            <p className="MainCond">{currentLocationWeatherInfo.condition}</p>
          </div>
          <WeatherForecast currentLocationForecastInfo={currentLocationForecastInfo}/>
        </div> : <Loading />}
      </div>
    );
  }
}