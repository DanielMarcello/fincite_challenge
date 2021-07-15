import React, { Component } from "react";
import './WeatherForecast.css'
import moment from "moment"

import { Typography, Skeleton } from "antd"

class Loading extends Component {
  render () {
    return (
      <div className="ForecastMain">
        <div className="ForecastGrid">
          {Array(5).fill(0).map((_, index) => (
            <div className="ForecastItem" key={`loading-${index}`}>
              <Skeleton.Input style={{ width: 200 }} active size={20} />
              <br/><br/>
              <Skeleton.Input style={{ width: 80 }} active size={20} />
              <br/><br/>
              <Skeleton.Input style={{ width: 200 }} active size={20} />
            </div>
          ))}
        </div>
      </div>
    )
  }
}

export default class WeatherForecast extends Component {
  constructor(props) {
    super(props);
    this.state = {};
  }

  render() {
    const {currentLocationForecastInfo} = this.props
    return (
      currentLocationForecastInfo ? (
        <div className="ForecastMain">
          {/* <p>{JSON.stringify(currentLocationForecastInfo)}</p> */}
          <div className="ForecastGrid">
            {currentLocationForecastInfo.map((forecast, index) => (
              <div className="ForecastItem" key={index}>
                <Typography.Title level={5} className="ForecastDay">
                    {moment(new Date(forecast.unix_last_update)).calendar()}
                </Typography.Title>
                <p className="ForecastTemp">{`${Math.round(forecast.temperature)}˚`}</p>
                <p className="ForecastCondition">{forecast.condition}</p>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <Loading />
      )
    );
  }
}