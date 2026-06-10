import { useParams } from 'react-router-dom'
export default function ResumeDetail() {
  const { id } = useParams()
  return <div>Resume Detail (/resumes/{id})</div>
}
