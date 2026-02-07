import { useState } from 'react'
import axios from 'axios'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const [formData, setFormData] = useState({
    study_hours: '',
    attendance: '',
    previous_grade: ''
  })
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const response = await axios.post(`${API_URL}/predict`, {
        study_hours: parseFloat(formData.study_hours),
        attendance: parseFloat(formData.attendance),
        previous_grade: parseFloat(formData.previous_grade)
      })
      setPrediction(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get prediction')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <div className="container">
        <h1>AcademiQ Grade Predictor</h1>
        <p className="subtitle">Predict student performance using ML</p>

        <form onSubmit={handleSubmit} className="prediction-form">
          <div className="form-group">
            <label htmlFor="study_hours">Study Hours per Week</label>
            <input
              type="number"
              id="study_hours"
              name="study_hours"
              value={formData.study_hours}
              onChange={handleChange}
              required
              min="0"
              max="168"
              step="0.1"
              placeholder="e.g., 15.5"
            />
          </div>

          <div className="form-group">
            <label htmlFor="attendance">Attendance (%)</label>
            <input
              type="number"
              id="attendance"
              name="attendance"
              value={formData.attendance}
              onChange={handleChange}
              required
              min="0"
              max="100"
              step="0.1"
              placeholder="e.g., 85.5"
            />
          </div>

          <div className="form-group">
            <label htmlFor="previous_grade">Previous Grade</label>
            <input
              type="number"
              id="previous_grade"
              name="previous_grade"
              value={formData.previous_grade}
              onChange={handleChange}
              required
              min="0"
              max="100"
              step="0.1"
              placeholder="e.g., 75.0"
            />
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Predicting...' : 'Predict Grade'}
          </button>
        </form>

        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        {prediction && (
          <div className="result-card">
            <h2>Prediction Result</h2>
            <div className="prediction-value">
              {prediction.predicted_grade.toFixed(2)}
            </div>
            <p className="result-label">Predicted Grade</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App