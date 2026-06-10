import { useParams } from 'react-router-dom'
export default function Rewrite() {
  const { task_id } = useParams()
  return <div>Rewrite (/rewrite/{task_id})</div>
}
