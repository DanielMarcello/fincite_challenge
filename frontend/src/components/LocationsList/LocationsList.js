import React, { Component } from "react";

import axios from 'axios';

import { Modal, Button, Input, Select, message, Skeleton } from 'antd';

import './LocationsList.css'

const ADD_LOCATION_API = 'http://0.0.0.0:8000/api/v1/locations/add_location/'


class Loading extends Component {
  render () {
    return (
      <div className="LocationsMain">
        <Skeleton.Input style={{ width: 100 }} active size={20} />
        <br/>
        <br/>
        <div className="IntervalsGrid">
          {Array(this.props.intervalNum).fill(0).map((_, index) => {
            return (
              <div key={`loading-section-${index}`} className="IntervalItem">
                <Skeleton.Input style={{ width: 200 }} active size={20} />
                <br/><br/><br/>
                <Skeleton.Input style={{ width: 150 }} active size={20} />
                <br/><br/>
                <Skeleton.Input style={{ width: 150 }} active size={20} />
                <br/><br/>
                <Skeleton.Input style={{ width: 150 }} active size={20} />
              </div>
            )
          })}
        </div>
      </div>
    )
  }
};


export default class LocationsList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      showModal: false,
      modalOkLoading: false,
      countryCode: null,
      city: null,
      tempIntervals: [
        {
          from: null,
          toInclusive: 10,
        },
        {
          from: 10,
          toInclusive: 16,
        },
        {
          from: 16,
          toInclusive: 24,
        },
        {
          from: 24,
          toInclusive: null,
        }
      ],
      locationsWeatherInfo: props.locationsWeatherInfo
    };
  }

  /**
    returns array of arrays according to temperature intervals
  */
  classifyLocations = () => {
    const {locationsWeatherInfo} = this.state
    if (!locationsWeatherInfo) {
      return [];
    }
    let tempIntervals = this.state.tempIntervals
    let classifiedLocations = Array.from(Array(tempIntervals.length), () => [])
    for (const locationWeather of locationsWeatherInfo) {
      const {city, country, last_weather_reading} = locationWeather
      const data = {
        fullName: `${city}, ${country.name} (${country.code})`,
        temperature: Math.round(last_weather_reading.temperature),
        condition: last_weather_reading.condition
      }
      for (let i = 0; i < tempIntervals.length; i++) {
        if (!tempIntervals[i].from) {
          if (data.temperature <= tempIntervals[i].toInclusive) {
            classifiedLocations[i].push(data)
            break;
          }
        } else if (!tempIntervals[i].toInclusive) {
          if (data.temperature > tempIntervals[i].from) {
            classifiedLocations[i].push(data)
            break;
          }
        } else {
          if (data.temperature > tempIntervals[i].from && data.temperature <= tempIntervals[i].toInclusive) {
            classifiedLocations[i].push(data)
            break;
          }
        }
      }
    }
    return classifiedLocations;
  }

  /**
    value update on city change
  */
  onChangeCity = (e) => {
    this.setState({city: e.target.value})
  }

  /**
    value update on country change
  */
  onChangeCountry = (value) => {
    this.setState({countryCode: value})
  }

  /**
    shows modal
  */
  showModal = () => {
    this.setState({showModal: true})
  };

  /**
    adds new location:
    - not adding if location already exists in list
    - not adding if location does not exists and city is not found
    - if location does not exists adds it to location
  */
  handleOk = async () => {
    const {city, countryCode} = this.state
    if(!city || city === "") {
      alert('City is empty');
      return;
    }
    if(!countryCode) {
      alert('Country is empty');
      return;
    }
    this.setState({modalOkLoading: true})
    const newLocationData = await this.addNewLocation(city, countryCode)
    if (!newLocationData) {
        this.setState({modalOkLoading: false})
        return
    }
    let locationsWeatherInfo = this.state.locationsWeatherInfo
    locationsWeatherInfo.push(newLocationData)
    this.setState({
      showModal: false,
      modalOkLoading: false,
      locationsWeatherInfo
    })
    message.success('New location created');
  };

  /**
    hides modal
  */
  handleCancel = () => {
    this.setState({showModal: false})
  };

  /**
    normalize text
  */
  normalizeText = (text) => {
    return text.normalize("NFD").replace(/\p{Diacritic}/gu, "").toLowerCase()
  }

  /**
    requests to add new location from API
  */
  addNewLocation = async (city, countryCode) => {
    const {locationsWeatherInfo} = this.state
    const normalizedCityInput = this.normalizeText(city);
    const locationExists = locationsWeatherInfo.find(
      location => location.country.code === countryCode && this.normalizeText(location.city) === normalizedCityInput
    )
    if (locationExists) {
      const {city, country} = locationExists
      alert(`${city}, ${country.name} (${country.code}) already exists.`)
      return null
    }
    const newLocationData = await this.requestNewLocation(city, countryCode);
    if (newLocationData.status !== 201) {
      alert(newLocationData.data.join("\n"));
      return null
    }
    return newLocationData.data
  }

  /**
    returns new location from API
  */
  requestNewLocation = async (city, countryCode) => {
    try {
      const newLocationData = await axios.post(
        ADD_LOCATION_API,
        {
          city: city,
          country_code: countryCode
        }
      )
      return newLocationData
    } catch (err) {
      return err.response
    }
  }

  /**
    renders locations DOM
  */
  renderLocations = (locationsList, mainIndex) => {
    return locationsList.map((location, index) => (
      <div key={`location-${mainIndex}${index}`} className="LocationsGrid">
        <div className="LocationItem">
          <span>{location.fullName}</span>
        </div>
        <div className="LocationItem">
          <span>{`${location.temperature}˚`}</span>
        </div>
        <div className="LocationItem">
          <span>{location.condition}</span>
        </div>
      </div>
    ))
  }

  static getDerivedStateFromProps = (nextProps, prevState) => {
    let newState = prevState
    newState.locationsWeatherInfo = nextProps.locationsWeatherInfo
    return newState;
  }

  render() {
    const { allCountriesInfo } = this.props
    const { tempIntervals, locationsWeatherInfo } = this.state
    let classifiedLocations = this.classifyLocations()
    return (
      locationsWeatherInfo ? (
        <div className="LocationsMain">
          {allCountriesInfo ? (
            <>
              <Button type="primary" onClick={this.showModal}>
                Add new location
              </Button>
              <Modal
                title="New Location"
                visible={this.state.showModal}
                confirmLoading={this.state.modalOkLoading}
                onOk={this.handleOk}
                onCancel={this.handleCancel}
                filterOption={(input, option) =>
                  option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
                }
              >
                <Input.Group compact>
                  <Select
                    style={{ width: '45%' }}
                    showSearch
                    placeholder="Select a country"
                    optionFilterProp="children"
                    onChange={this.onChangeCountry}
                  >
                    {allCountriesInfo.map(country => (
                      <Select.Option
                        key={country.code}
                        value={country.code}
                      >
                        {country.name}
                      </Select.Option>
                    ))}
                  </Select>
                  <Input
                    style={{ width: '55%' }}
                    placeholder="Type a city"
                    value={this.state.city}
                    onChange={this.onChangeCity}
                  />
                </Input.Group>
              </Modal>
          </>
          ): null}
          <div className="IntervalsGrid">
            {/* <p>{JSON.stringify(locationsWeatherInfo)}</p> */}
            {tempIntervals.map((interval, index) => {
              if (!interval.from) {
                return (
                  <div key={`section-${index}`} className="IntervalItem">
                    <h2>{`Less than equals ${interval.toInclusive}`}</h2>
                    {this.renderLocations(classifiedLocations[index])}
                  </div>
                )
              } else if (!interval.toInclusive) {
                return (
                  <div key={`section-${index}`} className="IntervalItem">
                    <h2>{`Greater than ${interval.from}`}</h2>
                    {this.renderLocations(classifiedLocations[index])}
                  </div>
                )
              } else {
                return (
                  <div key={`section-${index}`} className="IntervalItem">
                    <h2>{`Greater than ${interval.from}, Less than equals ${interval.toInclusive}`}</h2>
                    {this.renderLocations(classifiedLocations[index])}
                  </div>
                )
              }
            })}
          </div>
        </div>
      ) : <Loading intervalNum={this.state.tempIntervals.length}/>
    );
  }
}