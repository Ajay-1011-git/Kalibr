import { useParams } from 'react-router-dom'
export default function InterviewPrep() {
  const { id } = useParams()
  return <div>Interview Prep (/interview/{id})</div>
}
