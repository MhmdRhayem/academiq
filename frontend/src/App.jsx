import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [inputCourses, setInputCourses] = useState([])
  const [outputCourses, setOutputCourses] = useState([])
  const [grades, setGrades] = useState({})
  const [predictions, setPredictions] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [initializing, setInitializing] = useState(true)

  useEffect(() => {
    loadCourses()
    loadModelInfo()
  }, [])

  const loadCourses = async () => {
    try {
      const [inputRes, outputRes] = await Promise.all([
        axios.get(`${API_URL}/courses/input`),
        axios.get(`${API_URL}/courses/output`)
      ])

      setInputCourses(inputRes.data.courses)
      setOutputCourses(outputRes.data.courses)

      // Initialize all grades to 50 (default)
      const initialGrades = {}
      inputRes.data.courses.forEach(course => {
        initialGrades[course] = 50
      })
      setGrades(initialGrades)
    } catch (err) {
      setError('Failed to load course information')
    } finally {
      setInitializing(false)
    }
  }

  const loadModelInfo = async () => {
    try {
      const res = await axios.get(`${API_URL}/model/info`)
      setModelInfo(res.data)
    } catch (err) {
      console.error('Failed to load model info:', err)
    }
  }

  const handleGradeChange = (course, value) => {
    setGrades(prev => ({
      ...prev,
      [course]: parseFloat(value) || 0
    }))
  }

  const setAllGrades = (value) => {
    const newGrades = {}
    inputCourses.forEach(course => {
      newGrades[course] = parseFloat(value) || 0
    })
    setGrades(newGrades)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/predict`, { grades })
      setPredictions(response.data.predictions)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get prediction')
    } finally {
      setLoading(false)
    }
  }

  if (initializing) {
    return (
      <div className="app">
        <div className="container">
          <div className="loading">Loading course data...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="app">
      <div className="container">
        <h1>AcademiQ Grade Predictor</h1>
        <p className="subtitle">Predict S5-S6 grades based on S1-S4 performance</p>

        {modelInfo && (
          <div className="model-info">
            <strong>Model:</strong> {modelInfo.model_name} |
            <strong> R² Score:</strong> {modelInfo.metrics.r2.toFixed(3)} |
            <strong> RMSE:</strong> {modelInfo.metrics.rmse.toFixed(2)}
          </div>
        )}

        <form onSubmit={handleSubmit} className="prediction-form">
          <div className="bulk-actions">
            <label>Quick Fill All Grades:</label>
            <div className="quick-buttons">
              <button type="button" onClick={() => setAllGrades(50)}>50</button>
              <button type="button" onClick={() => setAllGrades(60)}>60</button>
              <button type="button" onClick={() => setAllGrades(70)}>70</button>
              <button type="button" onClick={() => setAllGrades(80)}>80</button>
              <button type="button" onClick={() => setAllGrades(90)}>90</button>
            </div>
          </div>

          <div className="courses-grid">
            {inputCourses.map(course => (
              <div key={course} className="course-input">
                <label htmlFor={course}>{course}</label>
                <input
                  type="number"
                  id={course}
                  value={grades[course] || 0}
                  onChange={(e) => handleGradeChange(course, e.target.value)}
                  min="0"
                  max="100"
                  step="0.1"
                />
              </div>
            ))}
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Predicting...' : 'Predict S5-S6 Grades'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {predictions && (
          <div className="results">
            <h2>Predicted S5-S6 Grades</h2>
            <div className="predictions-grid">
              {Object.entries(predictions).map(([course, grade]) => (
                <div key={course} className="prediction-item">
                  <div className="course-name">{course}</div>
                  <div className="grade-value">{grade.toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App