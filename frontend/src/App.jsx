import { useEffect, useState } from "react";
import { getJobs, getStats, addJob, updateJob, deleteJob } from "./api.js";

const STATUSES = ["applied", "interview", "offer", "rejected"];
const emptyForm = { company: "", role: "", status: "applied", notes: "" };

function App() {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState(null);
  const [filter, setFilter] = useState("");
  const [form, setForm] = useState(null); // null means the popup is closed
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  async function loadData() {
    try {
      const jobList = await getJobs(filter);
      const statsData = await getStats();
      setJobs(jobList);
      setStats(statsData);
      setError("");
    } catch (err) {
      setError(err.message);
    }
    setLoading(false);
  }

  // load again every time the filter changes
  useEffect(() => {
    loadData();
  }, [filter]);

  function openForm(job) {
    setError("");
    setForm(job);
  }

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function handleSave(e) {
    e.preventDefault();
    const { id, ...data } = form;
    try {
      if (id) {
        await updateJob(id, data);
      } else {
        await addJob(data);
      }
      setForm(null);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteJob(id);
      loadData();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app">
      <header>
        <div>
          <h1>PlaceTrack</h1>
          <p>Track every job application in one place</p>
        </div>
        <button className="primary" onClick={() => openForm(emptyForm)}>
          + Add application
        </button>
      </header>

      {error && !form && <div className="error">{error}</div>}

      {/* count cards */}
      <section className="cards">
        {["total", ...STATUSES].map((key) => (
          <div className={"card " + key} key={key}>
            <span>{key}</span>
            <strong>{stats ? stats[key] : "-"}</strong>
          </div>
        ))}
      </section>

      {/* filter buttons */}
      <div className="filters">
        {["", ...STATUSES].map((s) => (
          <button
            key={s}
            className={filter === s ? "chip active" : "chip"}
            onClick={() => setFilter(s)}
          >
            {s === "" ? "all" : s}
          </button>
        ))}
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Role</th>
              <th>Status</th>
              <th>Applied</th>
              <th>Notes</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loading && (
              <tr><td colSpan="6">Loading...</td></tr>
            )}
            {!loading && jobs.length === 0 && (
              <tr><td colSpan="6">No applications yet.</td></tr>
            )}
            {jobs.map((job) => (
              <tr key={job.id}>
                <td>{job.company}</td>
                <td>{job.role}</td>
                <td><span className={"badge " + job.status}>{job.status}</span></td>
                <td>{job.applied_on}</td>
                <td>{job.notes}</td>
                <td className="actions">
                  <button onClick={() => openForm(job)}>Edit</button>
                  <button className="danger" onClick={() => handleDelete(job.id)}>Delete</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* add / edit popup */}
      {form && (
        <div className="overlay" onClick={() => setForm(null)}>
          <form className="modal" onClick={(e) => e.stopPropagation()} onSubmit={handleSave}>
            <h2>{form.id ? "Edit application" : "New application"}</h2>

            {error && <div className="error">{error}</div>}

            <label>
              Company
              <input name="company" required maxLength={120} value={form.company} onChange={handleChange} />
            </label>
            <label>
              Role
              <input name="role" required maxLength={120} value={form.role} onChange={handleChange} />
            </label>
            <label>
              Status
              <select name="status" value={form.status} onChange={handleChange}>
                {STATUSES.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
            </label>
            <label>
              Notes
              <textarea name="notes" value={form.notes} onChange={handleChange} />
            </label>

            <div className="modal-actions">
              <button type="button" onClick={() => setForm(null)}>Cancel</button>
              <button className="primary" type="submit">Save</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

export default App;
